import datetime
import os
import subprocess
import uuid
from system_settings.models import SystemSetting

from user_event_logs.models import EventLog

def log(msg):
    print(msg)
    EventLog.debug(None, msg)

def authenticate():
    log("Getting authenticated...")
    subprocess.call(
        'gcloud auth activate-service-account --key-file=/credentials/ucsd-publichealth-justwalk.json', 
        shell=True
    )    
    log("Authenticated.")

def create_sample_report():
    log("Creating sample report...")
    local_path = str(uuid.uuid4())
    local_filename = '{}.csv'.format(uuid.uuid4())

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    local_filepath = os.path.join(local_path, local_filename)
    with open(local_filepath, 'w') as f:
        f.write('Hello, World!\n')
        f.write('Current date & time: ' + str(datetime.datetime.now()) + '\n')

    log("Created sample report.")
    return (local_path, local_filename)

def upload_all_files(local_path):
    log("Uploading all files...")

    GCLOUD_STORAGE_BUCKET = SystemSetting.get('GCLOUD_STORAGE_BUCKET_PUBLICDOCS')
    GCLOUD_STORAGE_PATH = SystemSetting.get('GCLOUD_STORAGE_PATH')
    web_path = 'gs://' + GCLOUD_STORAGE_BUCKET + '/' + GCLOUD_STORAGE_PATH
    log("Web path: " + web_path)
    subprocess.call(
        'gsutil -m cp -r ' + local_path + ' ' + web_path, 
        shell=True
    )
    log("Uploaded all files.")
    return web_path

def generate_url(local_path, local_filename):
    GCLOUD_STORAGE_BUCKET = SystemSetting.get('GCLOUD_STORAGE_BUCKET_PUBLICDOCS')
    GCLOUD_STORAGE_PATH = SystemSetting.get('GCLOUD_STORAGE_PATH')
    url = 'https://storage.googleapis.com/{}/{}/{}/{}'.format(GCLOUD_STORAGE_BUCKET, GCLOUD_STORAGE_PATH, local_path, local_filename)
    url = url.replace('//', '/')
    url = url.replace('/./', '/')
    return url

def remove_temporary_files(local_path):
    log("Removing temporary files...")
    subprocess.call(
        'rm -rf ' + local_path, 
        shell=True
    )
    log("Removed temporary files.")

def generate_report():
    authenticate()

    (local_path, local_filename) = create_sample_report()

    web_path = upload_all_files(local_path)

    log("Generated report bitbucket url: " + web_path + local_filename)

    url = generate_url(local_path, local_filename)

    log("Generated report public url: " + url)

    remove_temporary_files(local_path)