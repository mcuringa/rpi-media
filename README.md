# rpi-media

`rpi-media` is a Node/Express media server with a React kiosk client for driving two Raspberry Pi displays. The server accepts simple HTTP trigger URLs, broadcasts media events over WebSockets, and serves images, video, and audio to Chromium running in kiosk mode.

## Requirements

- Raspberry Pi OS with a desktop session for kiosk playback.
- Node.js 20.19 or newer. The installer uses Node.js 22 when needed.
- Chromium or `chromium-browser`.
- Media files placed under `apps/kiosk/media`.

## Media folders

Create the media folder and copy your project files into it:

```sh
mkdir -p apps/kiosk/media/maps
```

The default production server serves `apps/kiosk/media` at `/media`. Media can be mixed inside project folders:

```text
apps/kiosk/media/maps/title-card.jpg
apps/kiosk/media/maps/intro.mp4
apps/kiosk/media/maps/narration.mp3
```

## Local development

Install dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm --prefix apps/server install
npm --prefix apps/kiosk install
```

Start the API/WebSocket server on port `3000`:

```sh
npm --prefix apps/server run dev
```

In another terminal, start the kiosk frontend with Vite:

```sh
npm --prefix apps/kiosk run dev
```

Open the kiosk display URLs:

- Display 1: `http://localhost:5173/?display=1`
- Display 2: `http://localhost:5173/?display=2`

When the kiosk is running through Vite, it still connects to the server at `http://localhost:3000` by default.

## CircuitPython remote

Remote scripts live in `apps/remote` and can be copied to a mounted CircuitPython board:

```sh
invoke remote --name lux
```

Push all required CircuitPython libraries to the board first:

```sh
invoke remote-libs
```

For the VEML7700 lux sensor, this includes `adafruit_veml7700`. Pass `--circuitpy /path/to/CIRCUITPY` to either command if the drive is not auto-detected.

## Production build and server

Build the kiosk frontend:

```sh
npm --prefix apps/kiosk run build
```

Start the production server:

```sh
npm --prefix apps/server start
```

By default, the server listens on port `3000`, serves the built kiosk from `apps/kiosk/dist`, and serves media from `apps/kiosk/media`.

Optional environment variables:

```sh
PORT=3000 \
MEDIA_ROOT=/home/pi/rpi-media/apps/kiosk/media \
KIOSK_ROOT=/home/pi/rpi-media/apps/kiosk/dist \
npm --prefix apps/server start
```

Production kiosk URLs:

- Display 1: `http://localhost:3000/?display=1`
- Display 2: `http://localhost:3000/?display=2`

## Raspberry Pi install

Run the installer from the repo root on the Pi:

```sh
chmod +x install-rpi.sh
./install-rpi.sh
```

The installer:

- Installs Chromium, `xset`, `unclutter`, and Node.js when needed.
- Installs server and kiosk dependencies.
- Builds the kiosk frontend.
- Creates and starts the `rpi-media-server` systemd service.
- Installs a desktop autostart launcher for Chromium kiosk mode.

Useful installer variables:

```sh
DISPLAY_ID=1 PORT=3000 ./install-rpi.sh
DISPLAY_ID=2 PORT=3000 ./install-rpi.sh
APP_DIR=/home/pi/rpi-media INSTALL_USER=pi DISPLAY_ID=1 ./install-rpi.sh
```

`DISPLAY_ID` must be `1` or `2`. It controls the kiosk URL used by Chromium.

Check the server:

```sh
sudo systemctl status rpi-media-server
sudo journalctl -u rpi-media-server -f
curl http://localhost:3000/health
```

Restart after config or media changes:

```sh
sudo systemctl restart rpi-media-server
```

## Launch Chromium manually

If you want to test the kiosk without desktop autostart, launch Chromium from the Pi desktop session.

Display 1:

```sh
xset s off
xset -dpms
xset s noblank
unclutter -idle 0.5 -root &
chromium \
  --kiosk \
  --autoplay-policy=no-user-gesture-required \
  --disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --check-for-update-interval=31536000 \
  "http://localhost:3000/?display=1"
```


Display 2:

```sh
chromium \
  --kiosk \
  --autoplay-policy=no-user-gesture-required \
  --disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --check-for-update-interval=31536000 \
  "http://localhost:3000/?display=2"
```

The `xset` commands disable screen blanking and power management. The Chromium autoplay flags allow the kiosk to start video and audio playback from WebSocket-triggered events.

## Trigger media

The server accepts any HTTP method for trigger URLs. These examples use `curl`.

Show an image on display 1:

```sh
curl http://localhost:3000/api/img/d1/maps/title-card.jpg
```

Show a video on display 2:

```sh
curl http://localhost:3000/api/video/d2/maps/intro.mp4
```

Play audio:

```sh
curl http://localhost:3000/api/audio/maps/narration.mp3
```

The same triggers from Python with `requests`:

```python
import requests

server = "http://localhost:3000"

# Show an image on display 1.
requests.get(f"{server}/api/img/d1/maps/title-card.jpg").raise_for_status()

# Show a video on display 2.
requests.get(f"{server}/api/video/d2/maps/intro.mp4").raise_for_status()

# Play audio.
requests.get(f"{server}/api/audio/maps/narration.mp3").raise_for_status()
```

The API path declares the media type. The rest of the path is the file location under `apps/kiosk/media`, so `/api/video/d2/maps/intro.mp4` loads `apps/kiosk/media/maps/intro.mp4`.

Audio events are currently handled by display 1.
