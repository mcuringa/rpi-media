
import time
import requests

server = "http://localhost:3000"

delay = 5

# play spike.mp4 on display 1
requests.get(f"{server}/api/vid/test/spike.mp4")


