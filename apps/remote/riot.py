
import time

import config
import utils

server = config.media_url
print("Media server at:", server)

utils.connect_wifi()

session = utils.get_requests()

delay = 5

print("running riot remote")

# start NAS
session.get(f"{server}/api/video/d1/riots/news.mp4")
# get the time the video starts
start_time = time.time()

# end time is start_time + 5 minutes 20 seconds
end_time = start_time + 5 * 60 + 20

while time.time() <= end_time:
    session.get(f"{server}/api/img/d2/riots/flag.jpg")
    time.sleep(delay)
    session.get(f"{server}/api/img/d2/riots/looted.jpg")
    time.sleep(delay)
