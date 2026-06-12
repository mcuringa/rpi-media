# button.py
# Press a button wired between A0 and GND to trigger video playback.

import time

import adafruit_requests
import board
import digitalio
import neopixel
import socketpool
import wifi

import config


BUTTON_PIN = board.A0
DISPLAY = 1
VIDEO_PATH = "test/spike.mp4"
DEBOUNCE_SECONDS = 0.05
RETRIGGER_DELAY_SECONDS = 0.5


server = config.media_url
trigger_url = f"{server}/api/video/d{DISPLAY}/{VIDEO_PATH}"

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


def set_status(color):
    pixel[0] = color


def connect_wifi():
    print("Connecting to WiFi...")
    print(config.ssid, config.wifi_password)
    set_status((0, 0, 255))

    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)
    set_status((0, 255, 0))


def send_video_trigger(session):
    print("Triggering video:", trigger_url)
    set_status((255, 80, 0))

    response = session.get(trigger_url)
    try:
        print("Server response:", response.status_code)
        if response.status_code < 200 or response.status_code >= 300:
            set_status((255, 0, 0))
            return
    finally:
        response.close()

    set_status((0, 255, 0))


try:
    connect_wifi()
except Exception as error:
    print("Failed to connect:", error)
    set_status((255, 0, 0))
    raise

pool = socketpool.SocketPool(wifi.radio)
session = adafruit_requests.Session(pool)

print("Button remote ready")
print("Button pin:", BUTTON_PIN)
print("Video trigger:", trigger_url)

was_pressed = not button.value
last_change = time.monotonic()
armed = not was_pressed

if was_pressed:
    print("Button is pressed at startup. Release it to arm the trigger.")

while True:
    pressed = not button.value
    now = time.monotonic()

    if pressed != was_pressed and now - last_change >= DEBOUNCE_SECONDS:
        last_change = now
        was_pressed = pressed

        if not pressed and not armed:
            armed = True
            print("Button released; trigger armed.")
            set_status((0, 255, 0))

        if pressed and armed:
            try:
                send_video_trigger(session)
            except Exception as error:
                print("Failed to trigger video:", error)
                set_status((255, 0, 0))
                time.sleep(1)
                set_status((0, 255, 0))
            time.sleep(RETRIGGER_DELAY_SECONDS)

    time.sleep(0.01)
