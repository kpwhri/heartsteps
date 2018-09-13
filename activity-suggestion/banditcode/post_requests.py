import requests
import json


url = "http://localhost:5000/nightly"
payload = {
    "userId": '190238',
    "decisionId": '1803312',
    "array":  100
}

r = requests.post(url, data=payload)
print(r.text)
