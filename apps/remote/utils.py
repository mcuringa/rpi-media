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
print("SSID:", config.ssid)
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)



def connect_wifi():

    try:
        wifi.radio.connect(config.ssid, config.wifi_password)
        print("Connected!")
        print("IP address:", wifi.radio.ipv4_address)
        # set the pixel to green if connected
        pixel[0] = (0, 255, 0)
        time.sleep(3)
        # turn off the pixel after 3 seconds
        pixel[0] = (0, 0, 0)
    except Exception as e:
        print("Failed to connect:", e)
        # flash red if failed to connect
        while True:
            pixel[0] = (255, 0, 0)
            time.sleep(0.5)
            pixel[0] = (0, 0, 0)
            time.sleep(0.5)


def get_requests():
    pool = socketpool.SocketPool(wifi.radio)
    return requests.Session(pool)
