# Adafruit VEML7700 ambient light sensor:
# https://learn.adafruit.com/adafruit-veml7700

import adafruit_requests
import socketpool
import wifi
import neopixel
import config

import board
import adafruit_veml7700
import time

print("running gaza")
LED_STRIP_PIN = board.A3
LED_STRIP_COUNT = 23
LED_STRIP_ACTIVE_COUNT = 23
LED_STRIP_COLOR = (255, 255, 255)

# init led strip
led_strip = neopixel.NeoPixel(
    LED_STRIP_PIN,
    LED_STRIP_COUNT,
    brightness=0.6,
    auto_write=False,
)


def turn_on_led_strip():
    led_strip.fill((0, 0, 0))
    for index in range(LED_STRIP_ACTIVE_COUNT):
        led_strip[index] = LED_STRIP_COLOR
    led_strip.show()
    print("LED strip on:", LED_STRIP_ACTIVE_COUNT, "of",
          LED_STRIP_COUNT, "pixels on", LED_STRIP_PIN)

print("Turning on LED strip")
turn_on_led_strip()

# init lux sensor
i2c = board.STEMMA_I2C()
sensor = adafruit_veml7700.VEML7700(i2c)
print("Light sensor initialized:", sensor.lux, "lux")
min_lux = 100

print("Ambient light:", sensor.lux, "lux")
print("Minimum lux threshold:", min_lux, "lux")
time.sleep(1)


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
protest = f"{server}/api/video/d1/gaza/protest.mp4"
stats = f"{server}/api/img/d2/gaza/stats.gif"
clear_stats = f"{server}/api/clear/d2"

# test_img = f"{server}/api/img/d1/test/color-test.jpg"
# session.get(test_img, headers={"Connection": "close"})
# print("Test Image URL:", test_img)


lux = sensor.lux

while True:
    # print("Ambient light:", sensor.lux, "lux")
    if lux < min_lux:
        print("sending trigger")
        lux = sensor.lux
        response = session.get(protest)
        print("Response:", response.status_code)
        response = session.get(stats)

        time.sleep(30)
        response = session.get(clear_stats)
        print("Clear display response:", response.status_code)
    lux = sensor.lux
    time.sleep(.1)
