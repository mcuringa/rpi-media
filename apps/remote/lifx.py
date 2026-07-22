# light switch code, will be moving out
import time
import adafruit_requests
import socketpool
import wifi

import board
import analogio
import neopixel
import utils

import config
LIFX_ID = "d073d5896ed2"
# max: 2.575
# min: .02

POT_PIN = board.A2
READ_DELAY = 0.2


def voltage(pin):
    # Convert 16-bit ADC reading to voltage (approximate); adjust Vref if needed
    return (pin.value * 3.3) / 65535.0
    # return pin.value



hues = {
    "red": 0,
    "red_orange": 15,
    "orange": 30,
    "yellow_orange": 45,
    "gold": 50,
    "yellow": 60,
    "chartreuse": 75,
    "yellow_green": 90,
    "green": 120,
    "spring_green": 150,
    "turquoise": 165,
    "cyan": 180,
    "sky_blue": 200,
    "azure": 210,
    "blue": 240,
    "deep_blue": 255,
    "indigo": 270,
    "violet": 285,
    "purple": 300,
    "magenta": 315,
    "rose": 340,
    "crimson": 350,
}
utils.connect_wifi()
requests = utils.get_requests()
base = "https://api.lifx.com/v1/lights"


def get_lights():
    response = requests.get("{base}/all", auth=(config.lifx, ""))
    x = response.json()
    return x


def toggle():
    response = requests.post(
        f"{base}/id:{LIFX_ID}/toggle", auth=(config.lifx, ""))
    return response.json()


def set_color(hue, sat=.8):
    url = f"{base}/id:{LIFX_ID}/state"
    if hue in hues:
        hue = hues[hue]
    color = f"hue:{hue} saturation:{sat}"
    payload = {
        "duration": 1,
        "fast": False,
        "color": color
    }
    headers = {
        "accept": "text/plain",
        "content-type": "application/json",
        "Authorization": f"Bearer {config.lifx}"
    }

    response = requests.put(url, json=payload, headers=headers)
    return response.json()


def set_brightness(brightness):
    url = f"{base}/id:{LIFX_ID}/state"

    payload = {
        "duration": 1,
        "fast": False,
        "brightness": float(brightness/100)
    }
    headers = {
        "accept": "text/plain",
        "content-type": "application/json",
        "Authorization": f"Bearer {config.lifx}"
    }

    response = requests.put(url, json=payload, headers=headers)
    return response.json()


def debounce(f, delay):
    last_call = 0

    def wrapper(*args, **kwargs):
        nonlocal last_call
        now = time.monotonic()
        if now - last_call >= delay:
            last_call = now
            return f(*args, **kwargs)
    return wrapper


def stop_effects():

    print("stopping effect")
    url = f"{base}/id:{LIFX_ID}/effects/off"
    headers = {"Authorization": f"Bearer {config.lifx}"}
    return requests.post(url, headers=headers).json()


stop_effects = debounce(stop_effects, 5)


server = config.media_url


pot = analogio.AnalogIn(POT_PIN)

print("Potentiometer test ready")
print("Pot pin:", POT_PIN)

vid_time = 30
past_v = -1

try:
    # print("Setting light to green")
    # set_color("green")
    # time.sleep(5)
    # print("Setting light to red")
    # set_color("red")
    while True:
        val = pot.value
        v = voltage(pot)
        print(f"Value: {val}  Voltage: {v:.3f} V")
        time.sleep(READ_DELAY)
        # if abs(v - past_v) > 0.5: #Currently 0.5 threshold, lower/raise to change sensitivity
        #     set_status((255, 0, 0))
        # else:
        #     set_status((0, 255, 0))
        past_v = v

        
except KeyboardInterrupt:
    pot.deinit()
