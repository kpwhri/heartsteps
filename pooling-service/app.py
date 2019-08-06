from flask import Flask
from flask import request
from flask import Response
from flask import json

import subprocess

app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update():
    users=[]

    if request.json and request.json['users'] and isinstance(request.json['users'], list):
        for _user in request.json['users']:
            users.append(str(_user))

    subprocess.Popen(
        "/pooling-service/update.sh --users='%s'" % (','.join(users)),
        shell=True
        )

    return 'Update started'

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port='8000'
        )
