from flask import Flask
from flask import request
from flask import Response
from flask import json

import subprocess

app = Flask(__name__)

def run_r_script(filename, request_object={}):
    response = subprocess.run(
        "Rscript %s '%s'" % (filename, json.dumps(request_object)),
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
        )
    try:
        response_json = json.loads(response.stdout)
        return json.dumps(response_json)
    except:
        return response.stdout, 400

@app.route('/initialize', methods=['POST'])
def initialize():
    return run_r_script('initialize.r', request.json)


@app.route('/decision', methods=['POST'])
def decision():
    return run_r_script('decision.r', request.json)

@app.route('/nightly', methods=['POST'])
def nightly():
    return run_r_script('nightly.r', request.json)


if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port='8000'
        )
