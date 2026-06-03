# mayors.py

import wifi
import board
import neopixel
import config
import adafruit_requests as requests
import socketpool
import time

server = config.media_url
print("Media server at:", server)

print("Connecting to WiFi...")
print(config.ssid, config.wifi_password)
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)

# Set color (R, G, B)
pixel[0] = (0, 0, 255)

try:
    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)
    pixel[0] = (0, 255, 0)
    time.sleep(2)
except Exception as e:
    print("Failed to connect:", e)
    pixel[0] = (255, 0, 0)


print("Starting mayors and maps media")

pool = socketpool.SocketPool(wifi.radio)
requests = requests.Session(pool)


delay = 5

# start NAS
requests.get(f"{server}/api/audio/mayors/nas.mp3")

# Dutch NY/colonial
requests.get(f"{server}/api/img/d1/mayors/dutch-west-india-1642.jpg")
requests.get(f"{server}/api/img/d2/mayors/leader-1660-stuyvesant.jpeg")
time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/lenape.jpeg")
requests.get(f"{server}/api/img/d2/mayors/mantus-1637.jpg")

time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/dutch-west-india-1642.jpg")
requests.get(f"{server}/api/img/d2/mayors/mayor-van-cortland-1689.jpeg")

time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/battle-of-brooklyn-1776.jpg")
requests.get(f"{server}/api/img/d2/mayors/mayor-1757-John_Cruger.jpeg")


# 19th century


time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/manhattan-1817.png")
requests.get(f"{server}/api/img/d2/mayors/mayor-1811-DeWitt_Clinton.jpeg")

time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/nyc-1850.jpg")
requests.get(f"{server}/api/img/d2/mayors/mayor-wood-1861.jpg")

time.sleep(delay)

requests.get(f"{server}/api/img/d2/mayors/boss-1870-tweed.jpeg")
requests.get(f"{server}/api/img/d2/mayors/five-points-map.png")

time.sleep(delay)


requests.get(f"{server}/api/img/d2/mayors/mayor-1920-laguardia.jpg")

time.sleep(delay)

requests.get(f"{server}/api/img/d2/mayors/mayor-1926-jimmy-walker.png")

time.sleep(delay)
requests.get(f"{server}/api/img/d2/mayors/mayor-koch-1980.png")

time.sleep(delay)

requests.get(f"{server}/api/img/d2/mayors/mayor-dinkins-1990.png")
time.sleep(delay)

requests.get(f"{server}/api/img/d1/mayors/citibike-launch.png")
requests.get(f"{server}/api/img/d2/mayors/mayor-bloomberg-2002.png")
