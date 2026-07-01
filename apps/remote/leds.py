import time

import board
import neopixel

try:
    import config
except ImportError:
    config = None


LED_COUNT = getattr(config, "led_count", 150)
LED_BRIGHTNESS = getattr(config, "led_brightness", 0.35)
LED_PIN_NAME = getattr(config, "led_pin", "A0")


def find_pin(name):
    pin = getattr(board, name, None)
    if pin:
        return pin

    fallback = getattr(board, "NEOPIXEL", None)
    if fallback:
        print("Pin", name, "not found; using board.NEOPIXEL")
        return fallback

    raise RuntimeError("Could not find LED pin. Set led_pin in config.py.")


pixels = neopixel.NeoPixel(
    find_pin(LED_PIN_NAME),
    LED_COUNT,
    brightness=LED_BRIGHTNESS,
    auto_write=False,
)


def show():
    pixels.show()


def clear():
    fill((0, 0, 0))


def fill(color):
    pixels.fill(color)
    show()


def set_led(index, color):
    if 0 <= index < LED_COUNT:
        pixels[index] = color
        show()


def color_wheel(position):
    position = 255 - (position % 256)

    if position < 85:
        return (255 - position * 3, 0, position * 3)
    if position < 170:
        position -= 85
        return (0, position * 3, 255 - position * 3)

    position -= 170
    return (position * 3, 255 - position * 3, 0)


def chase(color=(255, 255, 255), wait=0.03, spacing=8, cycles=3):
    for _ in range(cycles):
        for offset in range(spacing):
            pixels.fill((0, 0, 0))

            for index in range(offset, LED_COUNT, spacing):
                pixels[index] = color

            show()
            time.sleep(wait)


def rainbow(wait=0.02, cycles=1):
    for cycle in range(256 * cycles):
        for index in range(LED_COUNT):
            pixel_index = (index * 256 // LED_COUNT) + cycle
            pixels[index] = color_wheel(pixel_index)

        show()
        time.sleep(wait)


def wipe(color=(255, 255, 255), wait=0.01):
    clear()

    for index in range(LED_COUNT):
        pixels[index] = color
        show()
        time.sleep(wait)


def pulse(color=(255, 255, 255), steps=30, wait=0.02):
    for level in range(steps):
        scale = level / steps
        fill(tuple(int(channel * scale) for channel in color))
        time.sleep(wait)

    for level in range(steps, -1, -1):
        scale = level / steps
        fill(tuple(int(channel * scale) for channel in color))
        time.sleep(wait)


print("Running 150 LED controller")
print("LED pin:", LED_PIN_NAME)
print("LED count:", LED_COUNT)

try:
    while True:
        wipe((255, 0, 0))
        wipe((0, 255, 0))
        wipe((0, 0, 255))
        chase((255, 255, 255))
        rainbow()
        pulse((255, 120, 20))
        clear()
        time.sleep(0.5)
except KeyboardInterrupt:
    clear()
