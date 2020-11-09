from celery import shared_task
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail

from participants.models import Participant

@shared_task
def send_adherence_messages():
    n_sms = 0
    n_email = 0
    # for participant in Participant.objects.filter(heartsteps_id='test-chris').all():
    for participant in Participant.objects.exclude(user=None).all():

        if participant.adherence_install_app() is True:
            n_sms += 1
            body = ("Thank you for taking part in the HeartSteps study. "
                    "You can now download the HeartSteps mobile app from a link below:\n"
                    "Android devices: https://play.google.com/store/apps/details?id=net.heartsteps.kpw\n"
                    "Apple devices: https://appstore.com/heartsteps\n"
                    "Be sure you have your Entry Code from your welcome letter "
                    "(which we haven't included for your security).")
            process_sms_message(
                participant.user.contactinformation.phone_e164,
                body
            )

        if participant.adherence_no_fitbit_data() > 0:
            if participant.adherence_no_fitbit_data() == 48:
                n_sms += 1
                body = ("We've noticed that your Fitbit has not synced with "
                        "HeartSteps in a few days. Try opening the Fitbit app "
                        "on your phone to get it to sync, or, if you are "
                        "having problems with your Fitbit, please give us a "
                        f"call at { settings.STUDY_PHONE_NUMBER } and we'll help you. Thanks!")
                process_sms_message(
                    participant.user.contactinformation.phone_e164,
                    body
                )
            elif participant.adherence_no_fitbit_data() == 72:
                n_sms += 1
                body = ("We've noticed that your Fitbit has not synced with "
                        "HeartSteps in a few days. Try opening the Fitbit app "
                        "on your phone to get it to sync, or, if you are "
                        "having problems with your Fitbit, please give us a "
                        f"call at { settings.STUDY_PHONE_NUMBER } and we'll help you. Thanks!")
                process_sms_message(
                    participant.user.contactinformation.phone_e164,
                    body
                )
            elif participant.adherence_no_fitbit_data() == (24*7):
                n_email += 1
                body = ("Hi, Survey Team! The HeartSteps server noticed that "
                        f"{participant.heartsteps_id} has not synced their "
                        "Fitbit in over a week. Could you help them out with that?\n"
                        "Thanks! \n\n"
                        f"StudyID: {participant.heartsteps_id}\n\n"
                        f"Phone: {participant.user.contactinformation.phone_e164}")
                send_survey_email(body)

        if participant.adherence_app_use() > 0:
            if participant.adherence_app_use() == 96:
                n_sms += 1
                body = ("We notice you haven't used HeartSteps in a few days. "
                        "If you are having any difficulties using the app, "
                        f"please give us a call at { settings.STUDY_PHONE_NUMBER }, "
                        "and we can assist you. Thanks!")
                process_sms_message(
                    participant.user.contactinformation.phone_e164,
                    body
                )
            elif participant.adherence_app_use() == (24*7):
                n_email += 1
                body = ("Hi, Survey Team! The HeartSteps server noticed that "
                        f"{participant.heartsteps_id} has not used the HeartSteps"
                        "app in over a week. Could you help them out with that?\n\n"
                        "Thanks! \n\n"
                        f"StudyID: {participant.heartsteps_id}\n\n"
                        f"Phone: {participant.user.contactinformation.phone_e164}")
                send_survey_email(body)

    return f"Sent {n_email} SMS messages via Twilio and {n_email} emails via SendGrid"
