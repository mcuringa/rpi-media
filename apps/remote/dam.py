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

POT_PIN = board.A0
READ_DELAY = 0.2
WATER_LED_PIN = board.A3
WATER_LED_COUNT = 23
WATER_LED_BRIGHTNESS = 0.35
WATER_LED_COLOR = (0, 80, 255)
WATER_LED_INACTIVE_COLOR = (0, 2, 8)
WATER_LED_FADE_TIME = 1.0
WATER_LED_FADE_STEPS = 20
WATER_LED_SCHEDULE = (
    (0, (22,)),
    (11, (20,)),
    (20, (16, 13)),
    (37, (10, 9, 8, 7, 4)),
    (48, (0,)),
)

status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
water_pixels = neopixel.NeoPixel(
    WATER_LED_PIN,
    WATER_LED_COUNT,
    brightness=WATER_LED_BRIGHTNESS,
    auto_write=False,
)


def set_status(color):
    status_pixel[0] = color


def blend_color(start_color, end_color, progress):
    return tuple(
        int(start_color[channel] + (end_color[channel] - start_color[channel]) * progress)
        for channel in range(3)
    )


def set_water_pixels(colors):
    for index in range(WATER_LED_COUNT):
        water_pixels[index] = colors[index]
    water_pixels.show()


def fade_water_pixels(start_colors, end_colors, duration=WATER_LED_FADE_TIME):
    if duration <= 0:
        set_water_pixels(end_colors)
        return

    wait = duration / WATER_LED_FADE_STEPS
    for step in range(1, WATER_LED_FADE_STEPS + 1):
        progress = step / WATER_LED_FADE_STEPS
        for index in range(WATER_LED_COUNT):
            water_pixels[index] = blend_color(start_colors[index], end_colors[index], progress)
        water_pixels.show()
        time.sleep(wait)


def faucet_lights(duration=None, color=WATER_LED_COLOR, inactive_color=WATER_LED_INACTIVE_COLOR):
    if duration is None:
        duration = audio_time

    current_colors = [inactive_color] * WATER_LED_COUNT
    set_water_pixels(current_colors)
    start_time = time.monotonic()

    for timestamp, active_leds in WATER_LED_SCHEDULE:
        remaining = timestamp - (time.monotonic() - start_time)
        if remaining > 0:
            time.sleep(remaining)

        target_colors = []
        for index in range(WATER_LED_COUNT):
            if index in active_leds:
                target_colors.append(color)
            else:
                target_colors.append(inactive_color)

        fade_water_pixels(current_colors, target_colors)
        current_colors = target_colors

    remaining = duration - (time.monotonic() - start_time)
    if remaining > 0:
        time.sleep(remaining)


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



def start_audio():
    print("sending audio request")
    url = f"{server}/api/audio/dam/water.mp3"
    print("curl", url)
    response = requests.get(url, headers={"Connection": "close"})
    print("Response:", response.status_code)



set_status((0, 255, 0))

pot = analogio.AnalogIn(POT_PIN)

print("Potentiometer test ready")
print("Pot pin:", POT_PIN)

audio_time = 65
past_v = -1

try:
    while True:
        val = pot.value
        v = voltage(pot)
        print(f"Value: {val}  Voltage: {v:.3f} V")
        time.sleep(READ_DELAY)
        if abs(v - past_v) > 0.5: #Currently 0.5 threshold, lower/raise to change sensitivity
            set_status((255, 0, 0))
            start_audio()
            faucet_lights(audio_time)
        else:
            set_status((0, 255, 0))
        past_v = v

        
except KeyboardInterrupt:
    set_status((0, 0, 0))
    status_pixel.deinit()
    water_pixels.deinit()
    pot.deinit()
