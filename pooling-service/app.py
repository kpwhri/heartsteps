from flask import Flask
from flask import request
from flask import Response
from flask import json

import subprocess

import sys



app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update():
    users=[]

    if request.json and request.json['users'] and isinstance(request.json['users'], list):
        for _user in request.json['users']:
            users.append(str(_user))

    subprocess.Popen(
                    "/pooling-service/update.sh --users='%s'" % (','.join(users)),
                    shell=True,
                   
                   )
                   #print('This is error output', file=sys.stderr)
#print('This is standard output', file=sys.stdout)







    return '{}'.format('')
            
            #if response.returncode > 0:
#print(response.stdout)

#else:
#print(response.stdout)
#return


    return response.stdout

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port='8000'
        )
