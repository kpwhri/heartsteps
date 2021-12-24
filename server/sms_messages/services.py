
from participants.models import Participant, Study
from .clients import SMSClient
from .models import Contact
from .models import Message

class SMSService:

    class UnknownContact(RuntimeError):
        pass

    class ContactNotEnabled(RuntimeError):
        pass

    def __init__(self, contact=None, user=None, username=None, phone_number=None):
        try:
            if phone_number:
                contact = Contact.objects.get(number=phone_number)
            if username:
                contact = Contact.objects.get(user__username=username)
            if user:
                contact = Contact.objects.get(user=user)
        except Contact.DoesNotExist:
            contact = None
        if not contact:
            raise SMSService.UnknownContact('No contact')
        self.__contact = contact
        self.__user = contact.user
        
        self.__client = SMSClient()
        self.__participant = Participant.objects.filter(user=self.__user).first()
        if self.__participant:
            self.__cohort = self.__participant.cohort
            if self.__cohort:
                self.__study = self.__cohort.study
                if self.__study:
                    self.__client.try_to_replace_twilio(study=self.__study)
        
    def send(self, body):
        if not self.__contact.enabled:
            raise SMSService.ContactNotEnabled('Contact not enabled')
        message = Message.objects.create(
            recipient = self.__contact.number,
            sender = self.__client.phone_number,
            body = body
        )
        
        
        message_id = self.__client.send(
            number = self.__contact.number,
            body = body
        )
        message.external_id = message_id
        message.save()
        return message

    def get_messages(self):
        return self.__contact.messages

