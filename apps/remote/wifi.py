import wifi
import board
import neopixel
import config


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
except Exception as e:
    print("Failed to connect:", e)
    pixel[0] = (255, 0, 0)