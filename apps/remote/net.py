import adafruit_requests
import config
import socketpool
import wifi


print("Running network status check")

print("Current WiFi TX power:", wifi.radio.tx_power, "dBm")
wifi.radio.tx_power = 15
print("Test WiFi TX power:", wifi.radio.tx_power, "dBm")

print("Scanning for SSID:", config.ssid)
network_found = False
network_channel = None
networks = wifi.radio.start_scanning_networks()
try:
    for network in networks:
        if network.ssid == config.ssid:
            network_found = True
            network_channel = network.channel
            print("Network channel:", network.channel)
            print("Network signal:", network.rssi, "dBm")
            print("Network authentication:", network.authmode)
finally:
    wifi.radio.stop_scanning_networks()

if not network_found:
    raise RuntimeError("WiFi network not found: " + config.ssid)

print("Scan complete; connecting directly on channel:", network_channel)
wifi.radio.connect(
    config.ssid,
    config.wifi_password,
    channel=network_channel,
    timeout=15,
)
print("Connected!")
print("IP address:", wifi.radio.ipv4_address)
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)
status_url = f"{config.media_url}/health"
response = None

try:
    print("Checking kiosk server:", status_url)
    response = requests.get(status_url, headers={"Connection": "close"})
    print("HTTP status:", response.status_code)
    print("Server status:", response.json())
finally:
    if response is not None:
        response.close()
