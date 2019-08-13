
from .clients import SMSClient
from .models import Contact
from .models import Message

class SMSService:

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
            raise RuntimeError('No contact')
        self.__contact = contact
        self.__user = contact.user
        self.__client = SMSClient()
        
    def send(self, body):
        if not self.__contact.enabled:
            raise ContactNotEnabled('Contact not enabled')
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
