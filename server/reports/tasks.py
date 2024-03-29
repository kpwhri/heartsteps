import datetime
import pprint
import re
import pytz
from django.core.mail import EmailMessage
import os
import subprocess
import uuid

from participants.models import Study
from participants.services import ParticipantService

from .models import ReportDesign, ReportRecipients, ReportRenderLog, ReportType
from system_settings.models import SystemSetting

from user_event_logs.models import EventLog


def log(msg, log_message_list=None):
    msg = " > " + msg
    # print(msg)
    EventLog.debug(None, msg)
    if log_message_list:
        log_message_list.append(msg)


def authenticate():
    log("Getting authenticated...")
    subprocess.call(
        "gcloud auth activate-service-account --key-file=/credentials/ucsd-publichealth-justwalk.json",
        shell=True,
    )
    log("Authenticated.")


def create_sample_report():
    log("Creating sample report...")
    local_path = str(uuid.uuid4())
    local_filename = "{}.csv".format(uuid.uuid4())

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    local_filepath = os.path.join(local_path, local_filename)
    with open(local_filepath, "w") as f:
        f.write("Hello, World!\n")
        f.write("Current date & time: " + str(datetime.datetime.now()) + "\n")

    log("Created sample report.")
    return (local_path, local_filename)


def upload_all_files(local_path):
    log("Uploading all files...")

    GCLOUD_STORAGE_BUCKET = SystemSetting.get("GCLOUD_STORAGE_BUCKET_PUBLICDOCS")
    GCLOUD_STORAGE_PATH = SystemSetting.get("GCLOUD_STORAGE_PATH")
    web_path = "gs://" + GCLOUD_STORAGE_BUCKET + "/" + GCLOUD_STORAGE_PATH
    log("Web path: " + web_path)
    subprocess.call("gsutil -m cp -r " + local_path + " " + web_path, shell=True)
    log("Uploaded all files.")
    return web_path


def generate_url(local_path, local_filename):
    GCLOUD_STORAGE_BUCKET = SystemSetting.get("GCLOUD_STORAGE_BUCKET_PUBLICDOCS")
    GCLOUD_STORAGE_PATH = SystemSetting.get("GCLOUD_STORAGE_PATH")
    url = "https://storage.googleapis.com/{}/{}/{}/{}".format(
        GCLOUD_STORAGE_BUCKET, GCLOUD_STORAGE_PATH, local_path, local_filename
    )
    url = url.replace("//", "/")
    url = url.replace("/./", "/")
    return url


def remove_temporary_files(local_path):
    log("Removing temporary files...")
    subprocess.call("rm -rf " + local_path, shell=True)
    log("Removed temporary files.")


def send_email(subject, body, report_type: ReportType, file_list=None):
    log("Loading up the recipients for the report type[{}]...".format(report_type.name))

    recipients = [
        x.recipient_email
        for x in ReportRecipients.objects.filter(report_type=report_type).all()
    ]

    if recipients and len(recipients) > 0:
        log("Found {} recipients: {}".format(len(recipients), recipients))

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="justwalk@ucsd.edu",
            to=recipients,
            cc=["justwalk@ucsd.edu"],
            reply_to=["justwalk@ucsd.edu"],
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
    log(
        "Adding recipient[{}] to report type[{}]...".format(
            recipient_email, report_type.name
        )
    )
    ReportRecipients.objects.get_or_create(
        report_type=report_type, recipient_email=recipient_email
    )
    log(
        "Added recipient[{}] to report type[{}].".format(
            recipient_email, report_type.name
        )
    )


def generate_report():
    authenticate()

    report_type, _ = ReportType.objects.get_or_create(name="Sample Report")
    add_recipient(report_type, "ffee21@gmail.com")

    (local_path, local_filename) = create_sample_report()

    upload_all_files(local_path)

    url = generate_url(local_path, local_filename)

    log("Generated report public url: " + url)

    send_email(
        "JustWalk Report",
        "Report generated at: " + url,
        report_type,
        [os.path.join(local_path, local_filename)],
    )

    remove_temporary_files(local_path)


def render_report(study_name=None, report_name=None, params=None):
    logs = []
    log("Rendering report...", logs)
    if study_name:
        log("Getting study[{}]...".format(study_name), logs)
        study = Study.objects.get(name=study_name)
    else:
        log("No study specified, using 'None' study...", logs)
        study = None

    # try to find the latest report design
    report_design_db = ReportDesign.objects.filter(study=study).order_by("-created").first()

    # if there's none, generate the sample report design
    if report_design_db:
        log("Found report design.", logs)
        entire_report_design_json = report_design_db.design

        # use the sample report name if none is specified
        if not report_name:
            report_name = "Sample Report"

        # use the sample parameters if none are specified
        if not params:
            params = get_sample_report_params()

        # get the recipients list
        design_list = entire_report_design_json["reports"]

        # find the report design for the specified report name
        for a_design in design_list:
            if a_design["name"] == report_name:
                design = a_design
                break
        
        # not to be confused
        del a_design, design_list

        # get the recipients list
        recipients = design["recipients"]

        if recipients and len(recipients) > 0:
            log("Found {} recipients: {}".format(len(recipients), recipients))

            for recipient in recipients:
                log("Preparing email to recipient[{} <{}>]...".format(recipient['name'], recipient['email']))

                (rendered_subject, rendered_body) = render_report_email(recipient, params, entire_report_design_json, design)

                log("Rendering result: ", logs)
                log("  Subject: " + rendered_subject, logs)
                log("  Body: " + rendered_body, logs)
    else:
        log("No report design found. Terminating...", logs)

    ReportRenderLog.objects.create(
        report_design = report_design_db,
        log=logs)

def parse_sv(msg_str):
    return re.findall(r'\{\{([^}]+)\}\}', msg_str)

class AttachmentInfo:
    def __init__(self, id, filename, local_path, local_fullpath, link):
        self.id = id
        self.filename = filename
        self.local_path = local_path
        self.local_fullpath = local_fullpath
        self.link = link

    def upload(self):
        log("Uploading all files...")

        GCLOUD_STORAGE_BUCKET = SystemSetting.get("GCLOUD_STORAGE_BUCKET_PUBLICDOCS")
        GCLOUD_STORAGE_PATH = SystemSetting.get("GCLOUD_STORAGE_PATH")
        web_path = "gs://" + GCLOUD_STORAGE_BUCKET + "/" + GCLOUD_STORAGE_PATH
        log("Web path: " + web_path)
        subprocess.call("gsutil -m cp -r " + self.local_path + " " + web_path, shell=True)
        log("Uploaded all files.")

        self.uploaded = True

    def delete(self):
        log("Deleting all files...")
        subprocess.call("rm -rf " + self.local_path, shell=True)
        log("Deleted all files.")

        self.deleted = True


class RenderingParams:
    def __init__(self, recipient, params, entire_report_design_json, current_report_design):
        self.recipient = recipient
        self.params = params
        self.entire_report_design_json = entire_report_design_json
        self.current_report_design = current_report_design
        self.attachments = {}
    
    def add_attachment(self, attachment_info: AttachmentInfo):
        if hasattr(self.attachments, attachment_info.id):
            raise Exception("Attachment id[{}] already exists.".format(attachment_info.id))

        self.attachments[attachment_info.id] = attachment_info

class Renderer_:
    def recipient_renderer(keywords, rparam: RenderingParams):
        if keywords[1] == 'name':
            return rparam.recipient['name']
        elif keywords[1] == 'email':
            return rparam.recipient['email']
        elif keywords[1] == 'timezone':
            return rparam.recipient['timezone']
        else:
            return Renderer.unknown_keyword(keywords, rparam)
    
    def datetime_renderer(keywords, rparam: RenderingParams):
        if keywords[1] == 'recipient_local':
            rendering_timezone = rparam.recipient['timezone']
        elif keywords[1] == 'server':
            rendering_timezone = 'UTC'
        else:
            return Renderer.unknown_keyword(keywords, rparam)
        
        if keywords[2] == 'now':
            datetime_obj = datetime.datetime.now().astimezone(pytz.timezone(rendering_timezone))
        else:
            return Renderer.unknown_keyword(keywords, rparam)
        
        if keywords[3] == 'datetime':
            return datetime_obj.strftime('%Y-%m-%d %H:%M:%S %Z')
        elif keywords[3] == 'date':
            return datetime_obj.strftime('%Y-%m-%d')
        elif keywords[3] == 'time':
            return datetime_obj.strftime('%H:%M:%S')
        elif keywords[3] == 'timezone':
            return datetime_obj.strftime('%Z')
        elif keywords[3] == 'escaped_datetime':
            return datetime_obj.strftime('%Y%m%d_%H%M%S_%Z')
        else:
            return Renderer.unknown_keyword(keywords, rparam)

    def participant_renderer(keywords, rparam: RenderingParams):
        if 'username' in rparam.params:
            username = rparam.params['username']
        else:
            raise Exception("No username specified. To use '{}' special variable, please specify username in the report parameters.".format(".".join(keywords)))

        participant_service = ParticipantService(username = username)
        participant = participant_service.participant

        if keywords[1] == 'user':
            user = participant.user
        else:
            return Renderer.unknown_keyword(keywords, rparam)

        if keywords[2] == 'username':
            return user.username
        else:
            return Renderer.unknown_keyword(keywords, rparam)

    def __get_random_local_path():
        # generate random path
        local_path = str(uuid.uuid4())
        
        # create the directory to store the attachment file
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        
        return local_path

    def csv_attachment_generator(design, sv_values, rparam):
        log("Creating {} report...".format(design["name"]))

        local_path = Renderer_.__get_random_local_path()

        # render the filename
        rendered_filename, sv_values = Renderer.render(design["filename"], rparam, sv_values)
        local_fullpath = os.path.join(local_path, rendered_filename)
        
        # render the content
        rendered_lines = []
        for line in design["content"]:
            rendered_single_line, sv_values = Renderer.render(line, rparam, sv_values)
            rendered_lines.append(rendered_single_line)

        # write the content to the file
        with open(local_fullpath, "w") as f:
            rendered_lines = [line + "\n" for line in rendered_lines]
            f.writelines(rendered_lines)

        log("Created sample report.")

        attachment_info = AttachmentInfo(
            id=design["id"],
            filename=rendered_filename,
            local_path=local_path,
            local_fullpath=local_fullpath,
            link=generate_url(local_path, rendered_filename)
        )

        return attachment_info


class Renderer:
    renderer_dict = {
        'recipient': Renderer_.recipient_renderer,
        'datetime': Renderer_.datetime_renderer,
        'participant': Renderer_.participant_renderer,
    }

    attachment_generator_dict = {
        'csv': Renderer_.csv_attachment_generator,
    }

    def generate_attachment(attachment_id: str, sv_values: dict, rparam: RenderingParams):
        attachment_list = rparam.entire_report_design_json['attachments']

        # fetch the attachment design
        design = None
        for attachment in attachment_list:
            if attachment['id'] == attachment_id:
                design = attachment
        if not design:
            raise Exception("Attachment id[{}] not defined.".format(attachment_id))
        
        # depending on the attachment type, generate the attachment
        if design['type'] in Renderer.attachment_generator_dict:
            generator_handle = Renderer.attachment_generator_dict[design['type']]

            if generator_handle:
                generated_attachment = generator_handle(design, sv_values, rparam)
                generated_attachment.upload()

                rparam.add_attachment(generated_attachment)

                return rparam, sv_values
            else:
                raise Exception("Attachment type[{}] not supported.".format(design['type']))
        else:
            raise Exception("Attachment type[{}] not supported.".format(design['type']))

    def render(template_str: str, rparam: RenderingParams, sv_values: dict={}, max_depth=100):
        current_str = template_str

        depth = 0

        while depth < max_depth:
            depth += 1
            sv_list = parse_sv(current_str)

            if len(sv_list) == 0:
                return (current_str, sv_values)
            else:
                for sv in sv_list:
                    if sv in sv_values:
                        current_str = current_str.replace('{{' + sv + '}}', sv_values[sv])
                    if sv in rparam.entire_report_design_json['special_variables']:
                        current_str = current_str.replace('{{' + sv + '}}', rparam.entire_report_design_json['special_variables'][sv])
                    else:
                        keywords = sv.split('.')

                        if keywords[0] == "link":
                            attachment_id = keywords[1]

                            if attachment_id not in rparam.attachments:
                                rparam, sv_values = Renderer.generate_attachment(attachment_id, sv_values, rparam)
                            
                            current_str = current_str.replace('{{' + sv + '}}', rparam.attachments[attachment_id].link)
                        else:
                            sv_values[sv] = Renderer.render_sv(keywords, rparam)
                            current_str = current_str.replace('{{' + sv + '}}', sv_values[sv])
        
        raise Exception("Max depth reached. Current string: " + current_str)

    def render_sv(keywords, rparam):
        if keywords[0] in Renderer.renderer_dict:
            renderer = Renderer.renderer_dict[keywords[0]]

            if renderer:
                return renderer(keywords, rparam)
            else:
                return Renderer.unknown_keyword(keywords, rparam)
        else:
            return Renderer.unknown_keyword(keywords, rparam)

    def get_renderer(first_keyword):
        if first_keyword in Renderer.renderer_dict:
            return Renderer.renderer_dict[first_keyword]
        else:
            return None
    
    def unknown_keyword(keywords, rparam):
        return "[[Unknown keyword: {}]]".format(".".join(keywords))

    

def calculate_sv(sv: str, rparam: RenderingParams):
    keywords = sv.split('.')

    return Renderer.render_sv(keywords, rparam)
        
        

def render_report_email(recipient, params, entire_report_design_json, current_report_design):
    log("Rendering email...")

    # get the values for the special variables
    rparam = RenderingParams(recipient, params, entire_report_design_json, current_report_design)
    
    # render the subject and body
    rendered_subject, sv_values = Renderer.render(current_report_design['subject'], rparam, {})
    rendered_body, sv_values = Renderer.render(current_report_design['body'], rparam, sv_values)


    email = EmailMessage(
            subject=rendered_subject,
            body=rendered_body,
            from_email="justwalk@ucsd.edu",
            to=[recipient['email']],
            reply_to=["justwalk@ucsd.edu"],
        )
    if len(rparam.entire_report_design_json['attachments']) > 0:
        log("Trying to attach file...")
        for attachment_id in rparam.current_report_design['attachments']:
            if attachment_id not in rparam.attachments:
                rparam, sv_values = Renderer.generate_attachment(attachment_id, sv_values, rparam)
            attachment_obj = rparam.attachments[attachment_id]
            email.attach_file(attachment_obj.local_fullpath)
            log("  Attached file: {}".format(attachment_id))

    log("Sending...")
    email.send()

    for attachment_id in rparam.attachments:
        attachment_obj = rparam.attachments[attachment_id]
        attachment_obj.delete()

    return (
        rendered_subject,
        rendered_body
    )


def get_sample_report_params():
    return {
        'username': 'Jung-1001'
    }


def get_sample_report_design():
    sample_body = """Hello, {{recipient.name}}!

Your full named email is {{custom.recipient.named_email}}.
Queried participant's username is {{participant.user.username}}.
Link to the basic report for {{participant.user.username}} is here: {{link.attachment_participant_basic_report}}"""

    return {
        "meta": {"syntax": 1},
        "reports": [
            {
                "name": "Sample Report",
                "recipients": [
                    {"name": "Junghwan Park", "email": "jup014@eng.ucsd.edu", "timezone": "America/Los_Angeles"}
                ],
                "subject": "JustWalk Sample Report: {{datetime.recipient_local.now.datetime}}",
                "body": sample_body,
                "attachments": [
                    "attachment_participant_basic_report"
                ]
            }
        ],
        "special_variables": {
            "custom.recipient.named_email": "{{recipient.name}} <{{recipient.email}}>",
        },
        "attachments": [
            {
                "id": "attachment_participant_basic_report",
                "name": "Participant Basic Report",
                "type": "csv",
                "filename": "participant_basic_report_{{participant.user.username}}_{{datetime.recipient_local.now.escaped_datetime}}.csv",
                "content": [
                    "key,value",
                    "username,{{participant.user.username}}",
                ]
            }
        ]
    }