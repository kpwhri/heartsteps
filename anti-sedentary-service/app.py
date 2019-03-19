from flask import Flask
from flask import request
from flask import Response
from flask import json

import subprocess

app = Flask(__name__)

@app.route('/decision', methods=['POST'])
def decision():
    input = {
        'userid': request.json['userid'],
        'decisionid': request.json['decisionid'],
        'time': request.json['time'],
        'daystart': request.json['daystart'],
        'dayend': request.json['dayend'],
        'state': request.json['state'],
        'steps': request.json['steps'],
        'available': request.json['available']
    }

    response = subprocess.run(
        "Rscript decision.r '%s'" % (json.dumps(input)),
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
        )

    return response.stdout

@app.route('/nightly', methods=['POST'])
def nightly():
    input = {
        'userid': request.json['userid'],
        'decisionid': request.json['decisionid'],
        'time': request.json['time'],
        'daystart': request.json['daystart'],
        'dayend': request.json['dayend'],
        'state': request.json['state'],
        'steps': request.json['steps']
    }

    response = subprocess.run(
        "Rscript nightly.r '%s'" % (json.dumps(input)),
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
        )

    return response.stdout


if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port='8000'
        )
