#!/usr/bin/env bash
set -euo pipefail

APP_NAME="rpi-media"
SERVICE_NAME="rpi-media-server"
KIOSK_LAUNCHER="/usr/local/bin/rpi-media-kiosk"

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
INSTALL_USER="${INSTALL_USER:-${SUDO_USER:-$(id -un)}}"
INSTALL_GROUP="${INSTALL_GROUP:-$(id -gn "$INSTALL_USER")}"
DISPLAY_ID="${DISPLAY_ID:-1}"
PORT="${PORT:-3000}"
KIOSK_URL="${KIOSK_URL:-http://localhost:${PORT}/?display=${DISPLAY_ID}}"

log() {
    printf "\n[%s] %s\n" "$APP_NAME" "$*"
}

die() {
    printf "\n[%s] ERROR: %s\n" "$APP_NAME" "$*" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1
}

sudo_cmd() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

sudo_write_file() {
    local path="$1"
    local tmp

    tmp="$(mktemp)"
    cat > "$tmp"
    sudo_cmd install -m 0644 "$tmp" "$path"
    rm -f "$tmp"
}

node_is_new_enough() {
    need_cmd node || return 1

    node -e '
        const [major, minor] = process.versions.node.split(".").map(Number);
        process.exit(major > 20 || (major === 20 && minor >= 19) ? 0 : 1);
    '
}

require_repo_layout() {
    [ -f "$APP_DIR/apps/server/package.json" ] || die "Missing apps/server/package.json. Run this script from the repo root or set APP_DIR."
    [ -f "$APP_DIR/apps/kiosk/package.json" ] || die "Missing apps/kiosk/package.json. Run this script from the repo root or set APP_DIR."
}

install_system_packages() {
    log "Installing Raspberry Pi OS packages"
    sudo_cmd apt-get update
    sudo_cmd apt-get install -y ca-certificates curl x11-xserver-utils unclutter

    if ! sudo_cmd apt-get install -y chromium-browser; then
        sudo_cmd apt-get install -y chromium
    fi

    if ! node_is_new_enough; then
        log "Installing Node.js 22"
        curl -fsSL https://deb.nodesource.com/setup_22.x | sudo_cmd bash -
        sudo_cmd apt-get install -y nodejs
    fi

    node_is_new_enough || die "Node.js 20.19+ is required. Current node: $(node --version 2>/dev/null || printf 'not installed')"
    need_cmd npm || die "npm was not found after installing Node.js."
}

install_app() {
    log "Installing server dependencies"
    npm --prefix "$APP_DIR/apps/server" ci

    log "Installing kiosk dependencies"
    npm --prefix "$APP_DIR/apps/kiosk" ci

    log "Building kiosk frontend"
    npm --prefix "$APP_DIR/apps/kiosk" run build
}

install_server_service() {
    local node_bin
    node_bin="$(command -v node)"

    log "Installing systemd service: ${SERVICE_NAME}.service"
    sudo_write_file "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=RPI Media Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${INSTALL_USER}
WorkingDirectory=${APP_DIR}/apps/server
Environment=NODE_ENV=production
Environment=PORT=${PORT}
Environment=MEDIA_ROOT=${APP_DIR}/apps/kiosk/media
Environment=KIOSK_ROOT=${APP_DIR}/apps/kiosk/dist
ExecStart=${node_bin} src/index.js
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo_cmd systemctl daemon-reload
    sudo_cmd systemctl enable "$SERVICE_NAME"
    sudo_cmd systemctl restart "$SERVICE_NAME"
}

install_kiosk_launcher() {
    local user_home autostart_dir chromium_bin

    user_home="$(getent passwd "$INSTALL_USER" | cut -d: -f6)"
    [ -n "$user_home" ] || die "Could not find home directory for user ${INSTALL_USER}."

    if need_cmd chromium-browser; then
        chromium_bin="$(command -v chromium-browser)"
    elif need_cmd chromium; then
        chromium_bin="$(command -v chromium)"
    else
        die "Chromium was not found after package installation."
    fi

    log "Installing kiosk launcher"
    sudo_write_file "$KIOSK_LAUNCHER" <<EOF
#!/usr/bin/env bash
set -euo pipefail

xset s off >/dev/null 2>&1 || true
xset -dpms >/dev/null 2>&1 || true
xset s noblank >/dev/null 2>&1 || true
unclutter -idle 0.5 -root >/dev/null 2>&1 &

exec ${chromium_bin} \\
  --kiosk \\
  --autoplay-policy=no-user-gesture-required \\
  --disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies \\
  --noerrdialogs \\
  --disable-infobars \\
  --disable-session-crashed-bubble \\
  --check-for-update-interval=31536000 \\
  "${KIOSK_URL}"
EOF
    sudo_cmd chmod 0755 "$KIOSK_LAUNCHER"

    autostart_dir="${user_home}/.config/autostart"
    sudo_cmd install -d -o "$INSTALL_USER" -g "$INSTALL_GROUP" "$autostart_dir"

    sudo_write_file "${autostart_dir}/rpi-media-kiosk.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=RPI Media Kiosk
Exec=${KIOSK_LAUNCHER}
X-GNOME-Autostart-enabled=true
EOF
    sudo_cmd chown "$INSTALL_USER:$INSTALL_GROUP" "${autostart_dir}/rpi-media-kiosk.desktop"
}

print_summary() {
    log "Install complete"
    cat <<EOF

Server service:
  sudo systemctl status ${SERVICE_NAME}
  sudo journalctl -u ${SERVICE_NAME} -f

Kiosk URL:
  ${KIOSK_URL}

Media folders:
  ${APP_DIR}/apps/kiosk/media/img
  ${APP_DIR}/apps/kiosk/media/video
  ${APP_DIR}/apps/kiosk/media/audio

Trigger examples:
  curl http://localhost:${PORT}/api/img/d${DISPLAY_ID}/example.jpg
  curl http://localhost:${PORT}/api/video/d${DISPLAY_ID}/example.mp4
  curl http://localhost:${PORT}/api/audio/example.mp3

Reboot to test desktop autostart:
  sudo reboot

EOF
}

main() {
    require_repo_layout

    if [ "$DISPLAY_ID" != "1" ] && [ "$DISPLAY_ID" != "2" ]; then
        die "DISPLAY_ID must be 1 or 2."
    fi

    log "Installing from ${APP_DIR}"
    log "Kiosk user: ${INSTALL_USER}"
    log "Kiosk group: ${INSTALL_GROUP}"
    log "Display ID: ${DISPLAY_ID}"

    install_system_packages
    install_app
    install_server_service
    install_kiosk_launcher
    print_summary
}

main "$@"
