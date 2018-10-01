import requests
import json
import uuid

from django.conf import settings
from django.utils import timezone

from push_messages.models import User, Device, Message, MessageReceipt, SENT

class DeviceMissingError(Exception):
    """User doesn't have a registered or active device."""

class MessageSendError(Exception):
    """Raised when message fails to send"""

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'

class FirebaseMessageService():
    """
    Sends messages to a device from Firebase
    """

    def __init__(self, device):
        self.device = device

    def make_headers(self):
        if not settings.FCM_SERVER_KEY:
            raise ValueError('FCM SERVER KEY not set')

        return {
            'Authorization': 'key=%s' % settings.FCM_SERVER_KEY,
            'Content-Type': 'application/json'
        }

    def send(self, request):

        request['to'] = self.device.token
        request['priority'] = 'high'

        response = requests.post(
            FCM_SEND_URL,
            headers = self.make_headers(),
            json = request
        )

        if response.status_code == 200:
            json = response.json()
            if json['success'] == 1:
                return json['multicast_id']
        raise MessageSendError()

    def format_notification(self, body, title, data={}):
        request = {
            'data': data
        }
        request['data']['notification'] = {
            'title': title,
            'body': body
        }
        return request

    def format_data(self, data):
        request = {
            'data': data
        }
        return request


class PushkitMessageService():
    """
    Sends messages to a device through APNs
    """



class PushMessageService():
    """
    Handles sending messages to a user and creating message reciepts.
    """

    def __init__(self, user):
        self.user = user
        self.device = self.get_device_for_user(self.user)
        # map methods depending on device type.
        self._service = FirebaseMessageService(self.device)

    def get_device_for_user(self, user):
        try:
            device = Device.objects.get(user=user, active=True)
        except Device.DoesNotExist:
            raise DeviceMissingError()
        return device

    def init_message(self):
        return Message(
            id = uuid.uuid4(),
            recipient = self.user,
            device = self.device
        )

    def send(self, message, request):
        try:
            external_id = self._service.send(request)
        except:
            message.save()
            return False        
        message.external_id = external_id
        message.save()

        MessageReceipt.objects.create(
            message = message,
            time = timezone.now(),
            type = SENT
        )

        return True

    def send_notification(self, body, title=None, data={}):
        message = self.init_message()
        data['messageId'] = str(message.id)
        if title is None:
            title = "HeartSteps"
        request = self._service.format_notification(body, title, data)
        message.content = json.dumps(request)
        return self.send(message, request)

    def send_data(self, data):
        message = self.init_message()
        data['messageId'] = str(message.id)
        request = self._service.format_data(data)
        message.content = json.dumps(request)
        return self.send(message, request)
