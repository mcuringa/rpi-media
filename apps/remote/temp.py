# Adafruit SHT31-D temperature and humidity sensor:
# https://learn.adafruit.com/adafruit-sht31-d-temperature-and-humidity-sensor-breakout
import board
import adafruit_sht31d
import time

print("running temp")

i2c = board.STEMMA_I2C()
sensor = adafruit_sht31d.SHT31D(i2c)

while True:
    temperature_c = sensor.temperature
    temperature_f = temperature_c * 9 / 5 + 32
    humidity = sensor.relative_humidity

    print("Temperature:", temperature_c, "C")
    print("Temperature:", temperature_f, "F")
    print("Humidity:", humidity, "%")
    time.sleep(1)
