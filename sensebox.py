import requests
import json

headers = {'content-type': 'application/json'}
url = 'https://api.opensensemap.org/boxes/:senseboxID/data'
data = [{"sensor":"601a5dc108aa8a001c34e6e4", "value": 0},{"sensor":"601a5dc108aa8a001c34e6e3", "value":0}]

r = requests.post(url, json=data, headers=headers)

print(r.status_code)