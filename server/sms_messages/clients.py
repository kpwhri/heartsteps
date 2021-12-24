from django.conf import settings
from sms_messages.models import TwilioAccountInfo

from twilio.rest import Client

class SMSClient:

    phone_number = getattr(settings,'TWILIO_PHONE_NUMBER', None)

    def try_to_replace_twilio(self, study):
        self.__study = study
        query = TwilioAccountInfo.objects.filter(study=study)
        
        if query.exists():
            account_info = query.first()
            
            self.__TWILIO_ACCOUNT_SID = account_info.account_sid
            self.__TWILIO_AUTH_TOKEN = account_info.auth_token
        else:
            self.__TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
            self.__TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
        
        
    def send(self, number, body):
        if hasattr(self, '__study'):
            self.try_to_replace_twilio(self.__study)
        
        self.__client = Client(
            self.__TWILIO_ACCOUNT_SID,
            self.__TWILIO_AUTH_TOKEN
        )
            
        response = self.__client.messages.create(
            body = body,
            to = number,
            from_ = self.phone_number
        )
        return response.sid
