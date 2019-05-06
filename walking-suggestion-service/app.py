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
    stderr=subprocess.STDOUT,
    universal_newlines=True)

  if response.returncode > 0:
    raise RuntimeError(response.stdout)
  else:
    return response.stdout       
    
@app.route('/initialize', methods=['POST'])
def initialize():
    try:
        run_r_script('initialize.r', request.json)
        return "Successful Initialization"
    except RuntimeError as error:
        return repr(error), 400

@app.route('/decision', methods=['POST'])
def decision():
    try:
        return run_r_script('decision.r', request.json)
    except RuntimeError as error:
        return repr(error), 400

@app.route('/nightly', methods=['POST'])
def nightly():
    try:
        run_r_script('nightly.r', request.json)
        return "Successful Update"
    except RuntimeError as error:
        return repr(error), 400

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8080
        )
