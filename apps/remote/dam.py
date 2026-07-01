# the dam group
# Continuously read a potentiometer wired to A0 and print its value.

import time
import adafruit_requests
import socketpool
import wifi

import config
import board
import analogio
import neopixel

# max: 2.575
# min: .02

POT_PIN = board.A3
READ_DELAY = 0.2
WATER_LED_PIN = board.A0
WATER_LED_COUNT = 15
WATER_LED_BRIGHTNESS = 0.35
WATER_LED_COLOR = (0, 80, 255)

status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
water_pixels = neopixel.NeoPixel(
    WATER_LED_PIN,
    WATER_LED_COUNT,
    brightness=WATER_LED_BRIGHTNESS,
    auto_write=False,
)


def set_status(color):
    status_pixel[0] = color


def faucet_lights(duration=None, color=WATER_LED_COLOR):
    if duration is None:
        duration = vid_time

    wait = duration / WATER_LED_COUNT
    water_pixels.fill((0, 0, 0))
    water_pixels.show()

    for index in range(WATER_LED_COUNT):
        water_pixels[index] = color
        water_pixels.show()
        time.sleep(wait)


def voltage(pin):
    # Convert 16-bit ADC reading to voltage (approximate); adjust Vref if needed
    return (pin.value * 3.3) / 65535.0


server = config.media_url


def connect_wifi():
    print("Connecting to WiFi...")
    print("SSID:", config.ssid)

    wifi.radio.connect(config.ssid, config.wifi_password)
    print("Connected!")
    print("IP address:", wifi.radio.ipv4_address)
    pool = socketpool.SocketPool(wifi.radio)


    session = adafruit_requests.Session(pool)
    return session


requests = connect_wifi()



def start_video():
    print("sending video request")
    url = f"{server}/api/audio/dam/water.mp3"
    print("curl", url)
    response = requests.get(url, headers={"Connection": "close"})
    print("Response:", response.status_code)



set_status((0, 255, 0))

pot = analogio.AnalogIn(POT_PIN)

print("Potentiometer test ready")
print("Pot pin:", POT_PIN)

vid_time = 30
past_v = -1

try:
    while True:
        val = pot.value
        v = voltage(pot)
        print(f"Value: {val}  Voltage: {v:.3f} V")
        time.sleep(READ_DELAY)
        if abs(v - past_v) > 0.5: #Currently 0.5 threshold, lower/raise to change sensitivity
            set_status((255, 0, 0))
            start_video()
            faucet_lights(vid_time)
        else:
            set_status((0, 255, 0))
        past_v = v

        
except KeyboardInterrupt:
    set_status((0, 0, 0))
    status_pixel.deinit()
    water_pixels.deinit()
    pot.deinit()
