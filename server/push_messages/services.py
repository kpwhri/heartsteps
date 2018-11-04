import requests
import json
import uuid

from django.conf import settings
from django.utils import timezone

from push_messages.models import User, Device, Message, MessageReceipt

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'
ONESIGNAL_SEND_URL = 'https://onesignal.com/api/v1/notifications'

class DeviceMissingError(Exception):
    """User doesn't have a registered or active device."""

class MessageSendError(Exception):
    """Raised when message fails to send"""

class OnesignalMessageService():
    """
    Sends Push Notifications to OneSignal
    """

    def __init__(self, device):
        self.device = device

    def send(self, request):
        try:
            app_id = settings.ONESIGNAL_APP_ID
            api_key = settings.ONESIGNAL_API_KEY
        except:
            raise ValueError('Onesignal misconfigured')

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Basic %s' % (api_key)
        }

        request['app_id'] = app_id
        request['include_player_ids'] = [self.device.token]

        response = requests.post(
            ONESIGNAL_SEND_URL,
            headers = headers,
            json = request
        )

        if response.status_code == 200:
            json = response.json()
            return json['id']
        raise MessageSendError()

    def format_notification(self, body, title, data):
        return {
            'contents': {
                'en': body
            },
            'headings': {
                'en': title
            },
            'data': data
        }

    def format_data(self, data):
        return {
            'data': data,
            'content_available': True
        }


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

    DeviceMissingError = DeviceMissingError

    def __init__(self, user):
        self.user = user
        self.device = self.get_device_for_user(self.user)
        # map methods depending on device type.
        if self.device.type == 'onesignal':
            self._service = OnesignalMessageService(self.device)
        else:
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
            type = MessageReceipt.SENT
        )

        return message

    def send_notification(self, body, title=None, data={}):
        message = self.init_message()
        message.message_type = Message.NOTIFICATION
        data['messageId'] = str(message.id)
        if title is None:
            title = "HeartSteps"
        request = self._service.format_notification(body, title, data)
        message.content = json.dumps(request)
        return self.send(message, request)

    def send_data(self, data):
        message = self.init_message()
        message.message_type = Message.DATA
        data['messageId'] = str(message.id)
        request = self._service.format_data(data)
        message.content = json.dumps(request)
        return self.send(message, request)
