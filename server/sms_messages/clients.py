from django.conf import settings

from twilio.rest import Client

class SMSClient:

    def send(self, number, body):
        self.__client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        response = self.__client.messages.create(
            body = body,
            to = number,
            from_ = self.phone_number
        )
        return response.sid
