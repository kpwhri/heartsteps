import requests

if __name__ == "__main__":
    url = "http://0.0.0.5001"
    payload = {'some': 'data'}

    r = requests.post(url, json=payload)
    r.text
