import requests
import json


url = "http://localhost:5001/decision"
payload = {
    "userId": [ 1 ],
    "decisionId": [ 1803312 ] ,
    "time": [ "2018-10-12 10:10" ] ,
    "dayStart": [ "2018-10-12 8:00" ] ,
    "dayEnd": [ "2018-10-12 20:00" ]
}


r = requests.post(url, data=payload)
print(r.text)

