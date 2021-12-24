import requests
import json

# Task 1
USERNAME = 'SergNik38'

url = f'https://api.github.com/users/{USERNAME}/repos'

req = requests.get(url).json()

with open('task1.json', 'w') as file:
    json.dump(req, file)

# Task 2
#  https://api.nasa.gov/
#  Astronomy Picture of the Day API

url = 'https://api.nasa.gov/planetary/apod'
key = 'bYpUF15vz1CFKJbg25UtvZ3jOjnlgr9Xg6jMufUX'
request = requests.get(f'{url}?api_key={key}').json()

with open('task2.json', 'w') as f:
    json.dump(request, f)
