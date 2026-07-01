# Adafruit VEML7700 ambient light sensor:
# https://learn.adafruit.com/adafruit-veml7700

import adafruit_requests
import socketpool
import wifi

import config

import board
import adafruit_veml7700
import time

print("running our city")

i2c = board.STEMMA_I2C()
sensor = adafruit_veml7700.VEML7700(i2c)
print("Light sensor initialized:", sensor.lux, "lux")
min_lux = 200


server = config.media_url
def connect_wifi():
    print("Connecting to WiFi...")
    print("SSID:", config.ssid)

    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)


connect_wifi()
pool = socketpool.SocketPool(wifi.radio)
session = adafruit_requests.Session(pool)
url = f"{server}/api/audio/d1/audio/test/old-town.mp3"
# url = f"{server}/api/video/d1/riots/news.mp4"

print("Our City Audio URL:", url)
lux = sensor.lux

while True:
    print("Ambient light:", sensor.lux, "lux")
    if lux < min_lux: 
        print("sending trigger")
        lux = sensor.lux
        response = session.get(url, headers={"Connection": "close"})
        print("Our City Audio URL:", url)
        print("Response:", response.status_code)
        time.sleep(20)
    lux = sensor.lux
    time.sleep(.1)
