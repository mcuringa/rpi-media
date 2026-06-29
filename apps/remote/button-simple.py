# button-simple.py
# Press a button wired between A0 and GND to toggle an LED wired to A3.

import time

import board
import digitalio
import neopixel


BUTTON_PIN = board.A0
LED_PIN = board.A3
DEBOUNCE_SECONDS = 0.05


status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)


def set_status(color):
    status_pixel[0] = color


set_status((0, 255, 0))

button = digitalio.DigitalInOut(BUTTON_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(LED_PIN)
led.direction = digitalio.Direction.OUTPUT
led.value = True


print("Simple button LED ready")
print("Button pin:", BUTTON_PIN)
print("LED pin:", LED_PIN)

was_pressed = not button.value
last_change = time.monotonic()
armed = not was_pressed

if was_pressed:
    print("Button is pressed at startup. Release it to arm the toggle.")

try:
    while True:
        pressed = not button.value
        now = time.monotonic()

        if pressed != was_pressed and now - last_change >= DEBOUNCE_SECONDS:
            last_change = now
            was_pressed = pressed

            if not pressed and not armed:
                armed = True
                print("Button released. Toggle armed.")

            if not pressed:
                set_status((0, 255, 0))
                print("Button released.")

            if pressed and armed:
                set_status((255, 255, 0))
                led.value = not led.value
                print("Button pressed. LED is", "on" if led.value else "off")

        time.sleep(0.01)
except KeyboardInterrupt:
    led.value = False
    set_status((0, 0, 0))
    status_pixel.deinit()
    led.deinit()
    button.deinit()
