import uuid
import json

from django.conf import settings
from django.utils import timezone

from push_messages.clients import ApplePushClient, AppleDevelopmentPushClient, ClientBase, FirebaseMessageService, OneSignalClient
from push_messages.models import User, Device, Message, MessageReceipt
from push_messages.tasks import onesignal_get_received, onesignal_refresh_interval


class DeviceMissingError(Exception):
    """User doesn't have a registered or active device."""


class PushMessageService():
    """
    Handles sending messages to a user and creating message reciepts.
    """

    class MessageNotFound(RuntimeError):
        pass

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
        self._service = self.get_client(self.device)
        self.__client = self._service

    def get_client(self, device):
        client_types = {
            'apns': ApplePushClient,
            'apns-dev': AppleDevelopmentPushClient,
            'firebase': FirebaseMessageService,
            'onesignal': OneSignalClient
        }

        client = client_types.get(device.type)
        if client:
            return client(device)
        else:
            return ClientBase(device)

    def get_device_for_user(self, user):
        device = Device.objects.filter(
            user=user,
            active=True
        ) \
            .order_by('-created') \
            .first()
        if device:
            return device
        else:
            raise DeviceMissingError()

    def __send(self, message_type, body=None, title=None, collapse_subject=None, data={}, send_message_id_only=False):
        message = Message.objects.create(
            recipient=self.user,
            device=self.device,
            message_type=message_type,
            body=body,
            title=title,
            collapse_subject=collapse_subject
        )
        data['messageId'] = str(message.uuid)
        message.data = data
        message.save()

        data_to_send = message.data
        if send_message_id_only:
            data_to_send = {
                'messageId': data['messageId']
            }

        try:
            external_id = self.__client.send(
                body=message.body,
                title=message.title,
                collapse_subject=message.collapse_subject,
                data=data_to_send
            )
        except self.__client.MessageSendError as error:
            raise PushMessageService.MessageSendError(error)
        MessageReceipt.objects.create(
            message=message,
            time=timezone.now(),
            type=MessageReceipt.SENT
        )
        if external_id:
            message.external_id = external_id
            message.save()
            onesignal_get_received.apply_async(
                countdown=onesignal_refresh_interval(),
                kwargs={
                    'message_id': message.id
                }
            )
        return message

    def send_notification(self, body, title=None, collapse_subject=None, data={}, send_message_id_only=False):
        if title is None:
            title = "HeartSteps"
        data['body'] = body
        data['title'] = title
        data['collapse_subject'] = collapse_subject

        return self.__send(
            message_type=Message.NOTIFICATION,
            body=body,
            title=title,
            collapse_subject=collapse_subject,
            data=data,
            send_message_id_only=send_message_id_only
        )

    def send_data(self, data):
        return self.__send(
            message_type=Message.DATA,
            data=data
        )
