import requests
import json


url = "http://localhost:5001/decision"
payload = {
    "userid": [ 1 ],
    "decisionid": [ 1803312 ] ,
    "time": [ "2018-10-12 10:10" ] ,
    "daystart": [ "2018-10-12 8:00" ] ,
    "dayend": [ "2018-10-12 20:00" ] ,
    "state": [ 1 ],
    "steps": [ 10 ],
    "available": [ 1 ]
}


r = requests.post(url, json=payload)
print(r.text)


url = "http://localhost:5001/nightly"
payload = {
    "userid": [ 2 ],
    "decisionid": [ 1803312 ] ,
    "time": [ "2018-10-12 10:05" ] ,
    "daystart": [ "2018-10-12 8:00" ] ,
    "dayend": [ "2018-10-12 20:00" ] ,
    "state": [ 1 ],
    "steps": [ 20 ]
}


r = requests.post(url, json=payload)
print(r.text)
