from pathlib import Path
import os
import shutil
import socket
import subprocess
import time
import urllib.request

from invoke import task


ROOT = Path(__file__).resolve().parent
REMOTE_DIR = ROOT / "apps" / "remote"
CONFIG_LOCAL = REMOTE_DIR / "config.local.py"
SERVER_DIR = ROOT / "apps" / "server"
CHROMIUM_FLAGS = [
    "--autoplay-policy=no-user-gesture-required",
    "--disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies",
    "--noerrdialogs",
    "--disable-infobars",
    "--disable-session-crashed-bubble",
    "--check-for-update-interval=31536000",
    "--no-first-run",
]


def find_circuitpy() -> Path:
    candidates = []
    env_path = os.environ.get("CIRCUITPY")
    if env_path:
        candidates.append(Path(env_path))

    user = os.environ.get("USER")
    if user:
        candidates.extend(
            [
                Path("/media") / user / "CIRCUITPY",
                Path("/run/media") / user / "CIRCUITPY",
            ]
        )

    candidates.append(Path("/Volumes/CIRCUITPY"))

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise ValueError(
        "Could not find the CIRCUITPY volume. "
        "Set CIRCUITPY=/path/to/CIRCUITPY or pass --circuitpy. "
        f"Searched: {searched}"
    )


def remote_script_path(name: str) -> Path:
    script_name = name if name.endswith(".py") else f"{name}.py"
    if Path(script_name).name != script_name:
        raise ValueError("Remote script must be a .py file directly inside apps/remote.")

    script_path = REMOTE_DIR / script_name

    if script_path.name in {"config.py", "config.local.py"}:
        raise ValueError("Choose an executable remote script, not a config file.")

    if not script_path.exists():
        raise ValueError(f"Remote script does not exist: {script_path}")

    if script_path.suffix != ".py":
        raise ValueError("Remote script must be a .py file.")

    return script_path


def local_ip_addresses():
    addresses = set()
    hostname = socket.gethostname()

    for addrinfo in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
        address = addrinfo[4][0]
        if not address.startswith("127."):
            addresses.add(address)

    return sorted(addresses)


def server_environment(port, host):
    env = os.environ.copy()
    env["HOST"] = host
    if port:
        env["PORT"] = str(port)
    return env


def print_kiosk_urls(port):
    print("Kiosk display URLs:")
    print(f"  d1: http://localhost:{port}/?display=1")
    print(f"  d2: http://localhost:{port}/?display=2")
    print(f"  d1: http://127.0.0.1:{port}/?display=1")
    print(f"  d2: http://127.0.0.1:{port}/?display=2")
    for address in local_ip_addresses():
        print(f"  d1: http://{address}:{port}/?display=1")
        print(f"  d2: http://{address}:{port}/?display=2")
    print()


def find_chromium(chromium=None):
    if chromium:
        return chromium

    for command in ("chromium-browser", "chromium", "google-chrome", "google-chrome-stable"):
        path = shutil.which(command)
        if path:
            return path

    raise ValueError("Could not find Chromium. Pass --chromium /path/to/chromium.")


def wait_for_server(port, timeout=10):
    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/health"

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)

    raise TimeoutError(f"Server did not respond at {url} within {timeout} seconds.")


def chromium_args(chromium, port, display_id, fullscreen=False):
    profile_dir = Path("/tmp") / f"rpi-media-chromium-d{display_id}"
    profile_dir.mkdir(parents=True, exist_ok=True)
    fullscreen_flags = ["--kiosk"] if fullscreen else []

    return [
        chromium,
        f"--user-data-dir={profile_dir}",
        *CHROMIUM_FLAGS,
        *fullscreen_flags,
        f"http://localhost:{port}/?display={display_id}",
    ]


@task
def remote(ctx, name, circuitpy=None):
    """Copy apps/remote/NAME.py to CIRCUITPY/code.py and config.local.py to config.py."""
    del ctx

    script_path = remote_script_path(name)
    if not CONFIG_LOCAL.exists():
        raise ValueError(f"Missing local config: {CONFIG_LOCAL}")

    circuitpy_path = Path(circuitpy) if circuitpy else find_circuitpy()
    if not circuitpy_path.exists() or not circuitpy_path.is_dir():
        raise ValueError(f"CIRCUITPY path is not a directory: {circuitpy_path}")

    code_target = circuitpy_path / "code.py"
    config_target = circuitpy_path / "config.py"

    shutil.copy2(script_path, code_target)
    shutil.copy2(CONFIG_LOCAL, config_target)

    print(f"Copied {script_path.relative_to(ROOT)} -> {code_target}")
    print(f"Copied {CONFIG_LOCAL.relative_to(ROOT)} -> {config_target}")


@task(name="start-server")
def start_server(ctx, dev=False, port=None, host="0.0.0.0"):
    """Start the media server."""
    command = "npm run dev" if dev else "npm start"
    server_port = str(port or 3000)
    env = server_environment(port, host)

    print_kiosk_urls(server_port)

    with ctx.cd(SERVER_DIR):
        ctx.run(command, env=env)


@task(name="start-all")
def start_all(ctx, dev=False, port=None, host="0.0.0.0", chromium=None, fullscreen=False):
    """Start the media server and launch Chromium for display 1 and display 2."""
    del ctx

    server_port = str(port or 3000)
    npm_command = ["npm", "run", "dev"] if dev else ["npm", "start"]
    env = server_environment(port, host)
    chromium_path = find_chromium(chromium)

    print_kiosk_urls(server_port)
    print(f"Starting server: {' '.join(npm_command)}")
    server_process = subprocess.Popen(npm_command, cwd=SERVER_DIR, env=env)

    chromium_processes = []
    try:
        wait_for_server(server_port)

        for display_id in (1, 2):
            args = chromium_args(chromium_path, server_port, display_id, fullscreen=fullscreen)
            print(f"Launching Chromium d{display_id}: {' '.join(args)}")
            chromium_processes.append(subprocess.Popen(args))

        print()
        print("Server and Chromium are running. Press Ctrl-C to stop the server.")
        server_process.wait()
    except KeyboardInterrupt:
        print()
        print("Stopping server...")
    finally:
        if server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

        for process in chromium_processes:
            if process.poll() is None:
                process.terminate()
