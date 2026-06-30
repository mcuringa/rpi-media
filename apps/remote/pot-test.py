# pot-test.py
# Continuously read a potentiometer wired to A0 and print its value.

import time

import board
import analogio
import neopixel

POT_PIN = board.A0
READ_DELAY = 0.2

status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)


def set_status(color):
    status_pixel[0] = color


def voltage(pin):
    # Convert 16-bit ADC reading to voltage (approximate); adjust Vref if needed
    return (pin.value * 3.3) / 65535.0




set_status((0, 255, 0))

pot = analogio.AnalogIn(POT_PIN)

print("Potentiometer test ready")
print("Pot pin:", POT_PIN)

past_v = 0

try:
    while True:
        val = pot.value
        v = voltage(pot)
        print(f"Value: {val}  Voltage: {v:.3f} V")
        time.sleep(READ_DELAY)
        if abs(v - past_v) > 0.5:
            set_status((255, 0, 0))
        else:
            set_status((0, 255, 0))
        past_v = v
        
except KeyboardInterrupt:
    set_status((0, 0, 0))
    status_pixel.deinit()
    pot.deinit()
