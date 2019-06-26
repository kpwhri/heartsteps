from celery import shared_task
from datetime import datetime

from django.conf import settings

from participants.models import Participant
from sms_service.models import SendSMS
from sms_service.utils import send_twilio_message


def process_sms_message(to_number, body):
    sms = SendSMS()
    sms.to_number = to_number
    sms.body = body
    sms.from_number = settings.TWILIO_PHONE_NUMBER
    sent = send_twilio_message(to_number, body)
    sms.sms_sid = sent.sid
    sms.account_sid = sent.account_sid
    sms.status = sent.status
    sms.sent_at = datetime.now()
    sms.save()


@shared_task
def send_adherence_messages():
    n = 0
    # for participant in Participant.objects.exclude(user=None).all():
    for participant in Participant.objects.filter(heartsteps_id='test-chris').all():
        n += 1
        body = "Quick message from HeartSteps"
        process_sms_message(
            participant.user.contactinformation.phone_e164,
            body
        )
        print("Sending message to " + participant.heartsteps_id)
        # if participant.adherence_install_app is True:
        #     n += 1
        #     pass
        # if participant.adherence_no_fitbit_data > 0:
        #     n += 1
        #     pass
        # if participant.adherence_app_use > 0:
        #     n += 1
        #     pass
    return f"Sent {n} SMS messages via Twilio"
