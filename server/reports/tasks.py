import datetime
from django.core.mail import EmailMessage
import os
import subprocess
import uuid
from .models import ReportRecipients, ReportType
from system_settings.models import SystemSetting

from user_event_logs.models import EventLog
from django.core.mail import send_mail

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

def send_email(subject, body, report_type: ReportType, file_list=None):
    log("Loading up the recipients for the report type[{}]...".format(report_type.name))

    recipients = [x.recipient_email for x in ReportRecipients.objects.filter(report_type=report_type).all()]
    
    if recipients and len(recipients) > 0:
        log("Found {} recipients: {}".format(len(recipients), recipients))
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email='justwalk@ucsd.edu',
            to=recipients,
            cc=['justwalk@ucsd.edu'],
            reply_to=['justwalk@ucsd.edu']
        )
        if file_list:
            log("Trying to attach file...")
            for filepath in file_list:
                email.attach_file(filepath)
                log("  Attached file: {}".format(filepath))
            
        log("Sending...")
        email.send()
        log("Sent email.")
    else:
        log("No recipients found.")

def add_recipient(report_type: ReportType, recipient_email):
    log("Adding recipient[{}] to report type[{}]...".format(recipient_email, report_type.name))
    ReportRecipients.objects.get_or_create(report_type=report_type, recipient_email=recipient_email)
    log("Added recipient[{}] to report type[{}].".format(recipient_email, report_type.name))

def generate_report():
    authenticate()

    report_type, _ = ReportType.objects.get_or_create(name='Sample Report')
    add_recipient(report_type, 'ffee21@gmail.com')

    (local_path, local_filename) = create_sample_report()

    upload_all_files(local_path)

    url = generate_url(local_path, local_filename)

    log("Generated report public url: " + url)

    send_email("JustWalk Report", "Report generated at: " + url, report_type, [os.path.join(local_path, local_filename)])

    remove_temporary_files(local_path)