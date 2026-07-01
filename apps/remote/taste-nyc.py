# taste-nyc.py
# Press a button wired between A0 and GND to advance through a 5-pixel strip.
# Each press lights the next NeoPixel and triggers the next video.

import time

import adafruit_requests
import board
import digitalio
import neopixel
import socketpool
import wifi

import config


BUTTON_PIN = board.A0
LED_STRIP_PIN = board.A3
LED_STRIP_COUNT = 5
DISPLAY = 1
DEBOUNCE_SECONDS = 0.05
RETRIGGER_DELAY_SECONDS = 0.5

#list of videos in order
VIDEO_PATHS = (
    "tastes/tastes-1.mov",
    "tastes/tastes-2.mov",
    "tastes/tastes-3.mov",
    "tastes/tastes-4.mov",
    "tastes/tastes-5.mov",
)

#each pixel CAN be a different color, but for now they are all white
PIXEL_COLORS = (
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
)

server = config.media_url

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.6)
led_strip = neopixel.NeoPixel(LED_STRIP_PIN, LED_STRIP_COUNT, brightness=0.6)
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


def set_status(color):
    pixel[0] = color


def clear_strip():
    led_strip.fill((0, 0, 0))
    led_strip.show()


def light_step(index):
    clear_strip()
    if 0 <= index < LED_STRIP_COUNT:
        led_strip[index] = PIXEL_COLORS[index]
        led_strip.show()


def connect_wifi():
    print("Connecting to WiFi...")
    print(config.ssid, config.wifi_password)
    set_status((0, 0, 255))

    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)
    set_status((0, 255, 0))


def trigger_video(session, video_path):
    print("Triggering video:", video_path)
    set_status((255, 80, 0))
    session.get(f"{server}/api/video/d{DISPLAY}/{video_path}")
    set_status((0, 255, 0))


clear_strip()

try:
    connect_wifi()
except Exception as error:
    print("Failed to connect:", error)
    set_status((255, 0, 0))
    raise

pool = socketpool.SocketPool(wifi.radio)
session = adafruit_requests.Session(pool)

print("Taste NYC remote ready")
print("Button pin:", BUTTON_PIN)
print("Video steps:", len(VIDEO_PATHS))

was_pressed = not button.value
last_change = time.monotonic()
armed = not was_pressed
step_index = 0

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
                trigger_video(session, VIDEO_PATHS[step_index])
                light_step(step_index)
                step_index = (step_index + 1) % len(VIDEO_PATHS)
            except Exception as error:
                print("Failed to trigger video:", error)
                set_status((255, 0, 0))
                time.sleep(1)
                set_status((0, 255, 0))
            time.sleep(RETRIGGER_DELAY_SECONDS)

    time.sleep(0.01)
