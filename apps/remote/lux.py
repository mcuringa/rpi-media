# Adafruit VEML7700 ambient light sensor:
# https://learn.adafruit.com/adafruit-veml7700
import board
import adafruit_veml7700
import time

print("running lux")

i2c = board.STEMMA_I2C()
sensor = adafruit_veml7700.VEML7700(i2c)

while True:
    print("Ambient light:", sensor.lux, "lux")
    time.sleep(1)
