import board
import neopixel
import time
print("Hello, world")

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)

# Set color (R, G, B)
try:
    while True:
        pixel[0] = (0, 255, 0)
        time.sleep(.5)
        pixel[0] = (255, 0, 0)
        time.sleep(.5)
        pixel[0] = (0, 0, 255)
        time.sleep(.5)
        pixel[0] = (0, 0, 0)
        time.sleep(.5)
except Exception as e:
    print("Something went wrong:", e)
