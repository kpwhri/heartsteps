from flask import Flask
from flask import request
from flask import Response
from flask import json

import subprocess

app = Flask(__name__)

@app.route('/decision', methods=['POST'])
def decision():
    input = {
        'userId': request.form['userId'],
        'decisionId': request.form['decisionId'],
        'isDriving': request.form['isDriving'],
        'isActive': request.form['isActive'],
        'preStepCount': request.form['preStepCount'],
        'locationType': request.form['locationType'],
        'currentTemperature': request.form['currentTemperature'],
        'notificationsSentToday': request.form['notificationsSentToday']
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
        'userId': request.form['userId'],
        'decisionId': request.form['decisionId']
    }

    response = subprocess.run(
        "Rscript decision.r '%s'" % (json.dumps(input)),
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