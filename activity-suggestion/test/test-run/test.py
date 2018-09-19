import requests
import json

# initial
with open('start.json') as json_file:  
    data = json.load(json_file)

payload = json.dumps(data)
url = "http://localhost:5000/initialize"
headers = {'Content-Type': "application/json"}
response = requests.request("POST", url, data=payload, headers=headers)
print(response.text)


for day in range(10):
    
    for dt in range(5):
        
        filename = 'call_' + str(day+1) + '_' + str(dt+1) + '.json'
        with open(filename) as json_file:  
            data = json.load(json_file)
        
        payload = json.dumps(data)
        url = "http://localhost:5000/decision"
        headers = {'Content-Type': "application/json"}
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        
    # nightly update on day 1
    filename = 'update_' + str(day+1) + '.json'

    with open(filename) as json_file:  
        data = json.load(json_file)
    
    payload = json.dumps(data)
    url = "http://localhost:5000/nightly"
    headers = {'Content-Type': "application/json"}
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    
    
    
    



    








