import requests
import json


url = "http://localhost:5001"
payload = {
    'userId': '190238',
    'decisionId': '1803312' ,
    'time': '19381019091' ,
    'dayStart': '18937298371' ,
    'dayEnd': '1928312987',
}

r = requests.post(url, data=payload)
print(r.text)
