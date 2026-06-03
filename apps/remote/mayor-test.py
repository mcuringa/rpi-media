
import time
import requests

server = "http://localhost:3000"

delay = 5

# start NAS
requests.get(f"{server}/api/audio/mayors/nas.mp3")

# Dutch NY/colonial
requests.get(f"{server}/api/img/d1/mayors/dutch-west-india-1642.jpg")
requests.get(f"{server}/api/img/d2/mayors/leader-1660-stuyvesant.jpeg")
time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/lenape.jpeg")
requests.get(f"{server}/api/img/d2/mayors/mantus-1637.jpg")

time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/dutch-west-india-1642.jpg")
requests.get(f"{server}/api/img/d2/mayors/mayor-van-cortland-1689.jpeg")

time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/battle-of-brooklyn-1776.jpg")
requests.get(f"{server}/api/img/d2/mayors/mayor-1757-John_Cruger.jpeg")


# 19th century


time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/manhattan-1817.png")
requests.get(f"{server}/api/img/d2/mayors/mayor-1811-DeWitt_Clinton.jpeg")

time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/nyc-1850.jpg")
requests.get(f"{server}/api/img/d2/mayors/mayor-wood-1861.jpg")

time.sleep(delay)

requests.get(f"{server}/api/img/d1/mayors/five-points-map.png")
requests.get(f"{server}/api/img/d2/mayors/boss-1870-tweed.jpeg")


time.sleep(delay)

requests.get(f"{server}/api/img/d2/mayors/mayor-1926-jimmy-walker.png")

time.sleep(delay)
requests.get(f"{server}/api/img/d1/mayors/world-fair-1938.jpg")
requests.get(f"{server}/api/img/d2/mayors/mayor-1934-laguardia.jpg")

time.sleep(delay)
requests.get(f"{server}/api/img/d2/mayors/mayor-koch-1980.png")

time.sleep(delay)

requests.get(f"{server}/api/img/d2/mayors/mayor-dinkins-1990.png")
time.sleep(delay)

requests.get(f"{server}/api/img/d1/mayors/citibike-launch.png")
requests.get(f"{server}/api/img/d2/mayors/mayor-bloomberg-2002.png")
