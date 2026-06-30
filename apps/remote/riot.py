# button.py
# Press a button wired between A0 and GND to trigger video playback.
# Turn on a NeoPixel strip wired to A3 at startup.

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
LED_STRIP_COUNT = 23
LED_STRIP_ACTIVE_COUNT = 23
LED_STRIP_COLOR = (255, 255, 255)
RACE_SEQUENCE_LOOPS = 3
RACE_SEQUENCE_DELAY_SECONDS = 0.04
RACE_SEQUENCE_COLORS = (
    (255, 255, 255),
    (255, 120, 0),
    (90, 25, 0),
)
DISPLAY = 1
VIDEO_PATH = "test/spike.mp4"
DEBOUNCE_SECONDS = 0.05
RETRIGGER_DELAY_SECONDS = 0.5


server = config.media_url

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.6)
led_strip = neopixel.NeoPixel(
    LED_STRIP_PIN,
    LED_STRIP_COUNT,
    brightness=0.6,
    auto_write=False,
)
button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


def set_status(color):
    pixel[0] = color


def turn_on_led_strip():
    led_strip.fill((0, 0, 0))
    for index in range(LED_STRIP_ACTIVE_COUNT):
        led_strip[index] = LED_STRIP_COLOR
    led_strip.show()
    print("LED strip on:", LED_STRIP_ACTIVE_COUNT, "of",
          LED_STRIP_COUNT, "pixels on", LED_STRIP_PIN)


def run_race_sequence():
    print("Running race sequence:", RACE_SEQUENCE_LOOPS, "loops")
    active_count = min(LED_STRIP_ACTIVE_COUNT, LED_STRIP_COUNT)

    for _ in range(RACE_SEQUENCE_LOOPS):
        for lead_index in range(active_count):
            led_strip.fill((0, 0, 0))

            for offset, color in enumerate(RACE_SEQUENCE_COLORS):
                led_strip[(lead_index - offset) % active_count] = color

            led_strip.show()
            time.sleep(RACE_SEQUENCE_DELAY_SECONDS)

    turn_on_led_strip()


def connect_wifi():
    print("Connecting to WiFi...")
    print(config.ssid, config.wifi_password)
    set_status((0, 0, 255))

    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)
    set_status((0, 255, 0))


def send_media_trigger(session):
    print("button pressed")
    delay = 5

    set_status((255, 80, 0))
    run_race_sequence()

    session.get(f"{server}/api/video/d1/riots/news.mp4")
    # get the time the video starts
    start_time = time.time()

    # end time is start_time + 5 minutes 20 seconds
    max_loops = 10
    end_time = start_time + 5 * 60 + 20
    loop_count = 0
    imgs = [
        "arch.png",
        "weeks-map.png"
        "tint.png",
        "news.png",
        "black-transit.png",
        "glatt.png",
        "flag.jpg",
        "looted.jpg"
    ]

    while time.time() <= end_time and loop_count < max_loops:
        for img in imgs:
            session.get(f"{server}/api/img/d2/riots/{img}")
            time.sleep(delay)
        loop_count += 1

    set_status((0, 255, 0))


turn_on_led_strip()

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
                send_media_trigger(session)
            except Exception as error:
                print("Failed to trigger video:", error)
                set_status((255, 0, 0))
                time.sleep(1)
                set_status((0, 255, 0))
            time.sleep(RETRIGGER_DELAY_SECONDS)

    time.sleep(0.01)
