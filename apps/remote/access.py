# access media test

import time
import adafruit_requests
import socketpool
import wifi

import config
print("Running access NEW")


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

url = f"{server}/api/video/d1/access/ny1-segment.mp4"
print("Triggering:", url)

for attempt in range(3):
    response = None

    try:
        response = session.get(url, headers={"Connection": "close"})
        print("Response:", response.status_code)
        break
    except OSError as error:
        print("Request failed:", error)
        time.sleep(1)
    finally:
        if response:
            response.close()


print("Done")

while True:
    time.sleep(1)
