from flask import Flask
from flask import request
from flask import Response
from flask import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port='8000'
        )