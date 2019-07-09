from django.conf import settings

from twilio.rest import Client

class SMSClient:

    def __init__(self):
        self.__client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.__phone_number = settings.TWILIO_PHONE_NUMBER

    @property
    def number(self):
        return self.__phone_number

    def send(self, number, body):
        response = self.__client.messages.create(
            body = body,
            to = number,
            from_ = self.__phone_number
        )
        return response.sid
