import uuid, json

from django.conf import settings
from django.utils import timezone

from push_messages.clients import ApplePushClient, AppleDevelopmentPushClient, ClientBase, FirebaseMessageService
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
            'firebase': FirebaseMessageService
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

    def init_message(self):
        return Message(
            uuid = uuid.uuid4(),
            recipient = self.user,
            device = self.device
        )

    def __send(self, message, request):
        try:
            self.__client.send(request)
        except self.__client.MessageSendError as error:
            raise PushMessageService.MessageSendError(error)
        MessageReceipt.objects.create(
            message = message,
            time = timezone.now(),
            type = MessageReceipt.SENT
        )
        return message

    def send_notification(self, body, title=None, data={}):
        message = self.init_message()
        message.message_type = Message.NOTIFICATION
        data['messageId'] = str(message.uuid)
        if title is None:
            title = "HeartSteps"
        request = self._service.format_notification(body, title, data)
        message.content = json.dumps(request)
        message.save()

        return self.__send(message, request)

    def send_data(self, data):
        message = self.init_message()
        message.message_type = Message.DATA
        data['messageId'] = str(message.uuid)
        request = self._service.format_data(data)
        message.content = json.dumps(request)
        message.save()

        return self.__send(message, request)
