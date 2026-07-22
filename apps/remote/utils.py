import wifi
import config
import adafruit_requests
import socketpool

server = config.media_url
print("Media server at:", server)

def connect_wifi(timeout=15):
    if not wifi.radio.connected:
        wifi.radio.connect(
            config.ssid,
            config.wifi_password,
            timeout=timeout,
        )

    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)


def get_requests():
    pool = socketpool.SocketPool(wifi.radio)
    return adafruit_requests.Session(pool)
