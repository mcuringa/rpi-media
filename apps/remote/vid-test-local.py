
import time
import requests

server = "http://localhost:3000"

delay = 5

# start NAS
requests.get(f"{server}/api/vid/test/spike.mp4")
