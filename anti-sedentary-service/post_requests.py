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
print payload

r = requests.post(url, json=payload)
print(r.text)

test_payloads = [{
    "userid": ["test-pedja"],
    "decisionid": ["1e6e2181-8d3e-432f-8c35-23c6d7e309c0"],
    "time": ["2019-06-04 16:55"],
    "daystart": ["2019-06-04 8:00"],
    "dayend": ["2019-06-04 20:00"],
    "state": [1],
    "available": [1],
    "steps": [43]
}]
'''
    {
        "userid": ["test-user"],
        "decisionid": ["17d523c9-8904-4562-8c76-46666403d741"],
        "time": ["2019-05-03 10:05"],
        "daystart": ["2019-05-03 08:00"],
        "dayend": ["2019-05-03 20:00"],
        "state": [1],
        "available": [1],
        "steps": [7],
    },
    {
        "userid": ["test-user"],
        "decisionid": ["af4920f0-afd6-4440-a5fc-a1f951307160"],
        "time": ["2019-05-03 10:10"],
        "daystart": ["2019-05-03 08:00"],
        "dayend": ["2019-05-03 20:00"],
        "state": [1],
        "available": [1],
        "steps": [0]
    },
    {
        "userid": ["test-user"],
        "decisionid": ["dba4b6d0-3138-4fc3-a394-bac2b1a301e3"],
        "time": ["2019-05-03 10:15"],
        "daystart": ["2019-05-03 08:00"],
        "dayend": ["2019-05-03 20:00"],
        "state": [1],
        "available": [1],
        "steps": [0]
    }
]
'''

for payload in test_payloads:
    print payload
    r = requests.post(url, json=payload)
    print r.text

url = "http://localhost:5001/nightly"
payload = {
    "userid": [ 1 ],
    "decisionid": [ 1803312 ] ,
    "time": [ "2018-10-12 10:05" ] ,
    "daystart": [ "2018-10-12 8:00" ] ,
    "dayend": [ "2018-10-12 20:00" ] ,
    "state": [ 1 ],
    "steps": [ 20 ]
}

r = requests.post(url, json=payload)
print(r.text)
