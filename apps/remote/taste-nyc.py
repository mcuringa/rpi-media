# taste-nyc.py
# Press a button wired between A0 and GND to cycle through five taste videos.
# A 5-pixel NeoPixel strip wired to A3 shows which video is being triggered.

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
LED_BRIGHTNESS = 0.6
DISPLAY = 1
DEBOUNCE_SECONDS = 0.05
RETRIGGER_DELAY_SECONDS = 0.5

VIDEOS = (
    "tastes/tastes-1.mov",
    "tastes/tastes-2.mov",
    "tastes/tastes-3.mov",
    "tastes/tastes-4.mov",
    "tastes/tastes-5.mov",
)

#the LED colors can be changed here, but are currently set to all white
LED_COLORS = (
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
    (255, 255, 255),
)


server = config.media_url

region_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.6)
led_strip = neopixel.NeoPixel(
    LED_STRIP_PIN,
    LED_STRIP_COUNT,
    brightness=LED_BRIGHTNESS,
    auto_write=False,
)
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


def set_status(color):
    region_pixel[0] = color


def show_selected_video(index):
    led_strip.fill((0, 0, 0))
    led_strip[index] = LED_COLORS[index]
    led_strip.show()


def connect_wifi():
    print("Connecting to WiFi...")
    set_status((0, 0, 255))

    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)
    set_status((0, 255, 0))


def trigger_video(session, index):
    video_path = VIDEOS[index]
    trigger_url = f"{server}/api/video/d{DISPLAY}/{video_path}"

    print("Triggering video", index + 1, "of", len(VIDEOS), ":", video_path)
    show_selected_video(index)
    set_status((255, 80, 0))

    response = session.get(trigger_url)
    response.close()

    set_status((0, 255, 0))


led_strip.fill((0, 0, 0))
led_strip.show()

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
print("LED strip pin:", LED_STRIP_PIN)
print("Video count:", len(VIDEOS))

selected_index = -1
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
            selected_index = (selected_index + 1) % len(VIDEOS)

            try:
                trigger_video(session, selected_index)
            except Exception as error:
                print("Failed to trigger video:", error)
                set_status((255, 0, 0))
                time.sleep(1)
                set_status((0, 255, 0))

            time.sleep(RETRIGGER_DELAY_SECONDS)

    time.sleep(0.01)
