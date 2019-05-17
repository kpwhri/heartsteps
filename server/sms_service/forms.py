from datetime import datetime

from django import forms
from django.conf import settings

from .models import SendSMS
from .utils import send_twilio_message


class SendSMSForm(forms.ModelForm):


    class Meta:
        model = SendSMS
        fields = ('to_number', 'body')

    def process_sms_message(self):
        # call twilio with validated form data
        to_number = self.cleaned_data['to_number']
        body = self.cleaned_data['body']
        sent = send_twilio_message(to_number, body)
        send_sms = self.save(commit=False)
        send_sms.from_number = settings.TWILIO_PHONE_NUMBER
        send_sms.sms_sid = sent.sid
        send_sms.account_sid = sent.account_sid
        send_sms.status = sent.status
        send_sms.sent_at = datetime.now()
        send_sms.save()
