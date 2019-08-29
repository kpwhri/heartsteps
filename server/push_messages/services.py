import uuid, json

from django.conf import settings
from django.utils import timezone

from push_messages.clients import ApplePushClient, AppleDevelopmentPushClient, ClientBase, FirebaseMessageService, OneSignalClient
from push_messages.models import User, Device, Message, MessageReceipt

class DeviceMissingError(Exception):
    """User doesn't have a registered or active device."""

class PushMessageService():
    """
    Handles sending messages to a user and creating message reciepts.
    """

    class MessageSendError(RuntimeError):
        pass

    class UnknownClient(RuntimeError):
        pass

    DeviceMissingError = DeviceMissingError

    def __init__(self, user=None, username=None):
        if username:
            user = User.objects.get(username=username)
        self.user = user
        self.device = self.get_device_for_user(self.user)
        self._service = self.get_client()
        self.__client = self._service

    def get_client(self):
        client_types = {
            'apns': ApplePushClient,
            'apns-dev': AppleDevelopmentPushClient,
            'firebase': FirebaseMessageService,
            'onesignal': OneSignalClient
        }

        client = client_types.get(self.device.type)
        if client:
            return client(self.device)
        else:
            return ClientBase(self.device)

    def get_device_for_user(self, user):
        try:
            device = Device.objects.get(user=user, active=True)
        except Device.DoesNotExist:
            raise DeviceMissingError()
        return device

    def __send(self, message_type, body=None, title=None, collapse_subject=None, data={}):
        message = Message.objects.create(
            recipient = self.user,
            device = self.device,
            message_type = message_type,
            body = body,
            title = title,
            collapse_subject = collapse_subject
        )
        data['messageId'] = str(message.uuid)
        message.data = data
        message.save()

        try:
            external_id = self.__client.send(
                body = message.body,
                title = message.title,
                collapse_subject = message.collapse_subject,
                data = message.data
            )
        except self.__client.MessageSendError as error:
            message.delete()
            raise PushMessageService.MessageSendError(error)
        MessageReceipt.objects.create(
            message = message,
            time = timezone.now(),
            type = MessageReceipt.SENT
        )
        if external_id:
            message.external_id = external_id
            message.save()
        return message

    def send_notification(self, body, title=None, collapse_subject=None, data={}):
        if title is None:
            title = "HeartSteps"        
        data['body'] = body
        data['title'] = title
        data['collapse_subject'] = collapse_subject

        return self.__send(
            message_type = Message.NOTIFICATION,
            body = body,
            title = title,
            collapse_subject = collapse_subject,
            data = data   
        )

    def send_data(self, data):
        return self.__send(
            message_type = Message.DATA,
            data = data
        )
