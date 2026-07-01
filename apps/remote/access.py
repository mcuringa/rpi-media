# access media test

import time
import adafruit_requests
import socketpool
import wifi
import board
import digitalio
import neopixel
import config


print("Running access")

BUTTON_PIN = board.A0
DEBOUNCE_SECONDS = 0.05
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

server = config.media_url


def connect_wifi():
    print("Connecting to WiFi...")
    print("SSID:", config.ssid)

    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)


connect_wifi()

pool = socketpool.SocketPool(wifi.radio)
session = adafruit_requests.Session(pool)

def start_video():
    url = f"{server}/api/video/d1/access/ny-1.mov"
    print("curl", url)
    response = session.get(url, headers={"Connection": "close"})
    print("Response:", response.status_code)

was_pressed = not button.value
last_change = time.monotonic()
armed = not was_pressed

while True:
    pressed = not button.value
    now = time.monotonic()

    pressed = not button.value
    now = time.monotonic()

    if pressed != was_pressed and now - last_change >= DEBOUNCE_SECONDS:
        last_change = now
        was_pressed = pressed

        if not pressed and not armed:
            armed = True
            start_video()
            time.sleep(30)

        if not pressed:
            pass

        if pressed and armed:
            armed = not armed




    time.sleep(0.1)
