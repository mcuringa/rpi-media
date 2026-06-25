# button.py
# Press a button wired between A0 and GND to trigger video playback.
# Turn on an 8-pixel NeoPixel strip wired to A1 at startup.

import time

import adafruit_requests
import board
import digitalio
import neopixel
import socketpool
import wifi

import config


BUTTON_PIN = board.A0
LED_STRIP_PIN = board.A1
LED_STRIP_COUNT = 23
LED_STRIP_ACTIVE_COUNT = 23
LED_STRIP_COLOR = (255, 255, 255)
DISPLAY = 1
VIDEO_PATH = "test/spike.mp4"
DEBOUNCE_SECONDS = 0.05
RETRIGGER_DELAY_SECONDS = 0.5


server = config.media_url
trigger_url = f"{server}/api/video/d{DISPLAY}/{VIDEO_PATH}"

button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP





print("Button remote ready")
print("Button pin:", BUTTON_PIN)

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
            print("Button released. Trigger armed.")

        if pressed and armed:
            print("Button pressed. Triggering video playback.")
            time.sleep(RETRIGGER_DELAY_SECONDS)

    time.sleep(0.01)
