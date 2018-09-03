from flask import Flask
from flask import request
from flask import Response
from flask import json

import subprocess

app = Flask(__name__)

@app.route('/', methods=['POST'])
def decision():
    input = {
        'userId': request.form['userId'],
        'decisionId': request.form['decisionId'],
        'time': request.form['time'],
        'dayStart': request.form['dayStart'],
        'dayEnd': request.form['dayEnd']
    }

    response = subprocess.run(
        "Rscript example.r '%s'" % (json.dumps(input)),
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
