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

#Write function that starts video, ask it to stop listening to pot 
# while video is running, then restart listening after video is done.
def start_video():
    # Placeholder for starting video recording or playback
    #placeholder for stoping the listening of pot
    #placeholder for restarting the listening of pot after video is done
    return()


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
        if abs(v - past_v) > 0.5: #Currently 0.5 threshold, lower/raise to change sensitivity
            set_status((255, 0, 0))
            # HERE IS WHERE YOU START AUDIO/VISUAL
        else:
            set_status((0, 255, 0))
        past_v = v

        
except KeyboardInterrupt:
    set_status((0, 0, 0))
    status_pixel.deinit()
    pot.deinit()
