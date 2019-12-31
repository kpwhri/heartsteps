import csv
from datetime import datetime
import subprocess
from subprocess import check_output

from flask import Flask
from flask import request
from flask import Response

app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update():
    aim2 = get_aim2_from_request()
    aim3 = get_aim3_from_request()

    if aim2 or aim3:
        write_join_date_file(aim3)

        aim2_usernames = [u['username'] for u in aim2]
        subprocess.Popen(
            "/pooling-service/update.sh --users='%s'" % (','.join(aim2_usernames)),
            shell=True,
            universal_newlines=True
        )
        return 'running'
    return 'Not running', 400

@app.route('/update/aim3', methods=['POST'])
def update_aim3():
    aim3 = get_aim3_from_request()
    if aim3:
        write_join_date_file(aim3)
        subprocess.Popen(
            "/pooling-service/update_aim_three_testing.sh",
            shell=True,
            universal_newlines=True
        )
        return 'running'
    return 'Not running', 400


def get_participants_from_request():
    if request.json and request.json['participants'] and isinstance(request.json['participants'], list):
        return [u for u in request.json['participants'] if u['study'].upper() == 'KPWHRI']
    else:
        return []

def get_aim2_from_request():
    return [u for u in get_participants_from_request() if u['cohort'].upper() == 'AIM 2']

def get_aim3_from_request():
    return [u for u in get_participants_from_request() if u['cohort'].upper() == 'AIM 3']

def write_join_date_file(users):
    with open('data/join_dates.csv', 'w', newline='') as csvfile:
        fieldnames = ['user_id', 'join_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for user in users:
            start_date = datetime.strptime(user['start'], '%Y-%m-%d')
            writer.writerow({
                'user_id': user['username'],
                'join_date': start_date.strftime('%-m/%-d/%y')
            })

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port='8000'
    )
