from flask import Flask
from flask import request
from flask import Response
import sys

import subprocess
from subprocess import check_output

app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update():
    users=[]

    if request.json and request.json['users'] and isinstance(request.json['users'], list):
        for _user in request.json['users']:
            users.append(str(_user))

                # out =
    subprocess.Popen(
        "/pooling-service/update.sh --users='%s'" % (','.join(users)),
                     shell=True,stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     universal_newlines=True
    )
#.communicate()
    #print('This is error output', file=sys.stderr)
# out =subprocess.Popen.communicate()
#print(out)
    return 'gt'
#(resp.text, resp.status_code, resp.headers.items())

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port='8000'
    )