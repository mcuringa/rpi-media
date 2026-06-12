
import time
import requests

server = "http://localhost:3000"

delay = 5

print("running riot test")

# start NAS
requests.get(f"{server}/api/video/d1/riots/news.mp4")
# get the time the video starts
start_time = time.time()

# end time is start_time + 5 minutes 20 seconds
end_time = start_time + 5 * 60 + 20

while time.time() <= end_time:
    requests.get(f"{server}/api/img/d2/riots/flag.jpg")
    time.sleep(delay)
    requests.get(f"{server}/api/img/d2/riots/looted.jpg")
    time.sleep(delay)