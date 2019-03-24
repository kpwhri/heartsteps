import requests
import json

from apns2.client import APNsClient
from apns2.payload import Payload

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'

class ClientBase:

    class MessageSendError(RuntimeError):
        pass

    def __init__(self, device):
        self.device = device

    def send(self, request):
        return None

    def format_notification(self, body, title, data):
        notification = {
            'title': title,
            'body': body
        }
        return {**data, **notification}

    def format_data(self, data):
        return data
    

class ApplePushClient(ClientBase):

    def get_client(self):
        return APNsClient('/credentials/heartsteps-apns.pem')

    def send(self, request):
        payload = Payload(
            content_available=True,
            custom=request
        )
        client = self.get_client()
        client.send_notification(self.device.token, payload, 'com.nickreid.heartsteps.voip')

class AppleDevelopmentPushClient(ApplePushClient):

    def get_client(self):
        return APNsClient('/credentials/heartsteps-apns.pem', use_sandbox=True)

class FirebaseMessageService(ClientBase):
    """
    Sends messages to a device from Firebase
    """

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
        raise FirebaseMessageService.MessageSendError()

    def format_notification(self, body, title, data):
        notification = {
            'title': title,
            'body': body
        }
        return {
            'data': {**data, **notification}
        }

    def format_data(self, data):
        request = {
            'data': data
        }
        return request

class OneSignalClient(ClientBase):

    def __init__(self, device):
        self.device = device

        if not settings.ONESIGNAL_API_KEY:
            raise ImproperlyConfigured('No OneSignal API KEY')
        if not settings.ONESIGNAL_APP_ID:
            raise ImproperlyConfigured('No OneSignal APP ID')
        self.api_key = settings.ONESIGNAL_API_KEY
        self.app_id = settings.ONESIGNAL_APP_ID

    def send(self, request):
        
        response = requests.post(
            'https://onesignal.com/api/v1/notifications',
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % (self.api_key)
            },
            json = {
                'app_id': self.app_id,
                'include_player_ids': [self.device.token],
                'contents': {
                    'en': request['body']
                },
                'headings': {
                    'en': request['title']
                },
                'data': request
            }
        )

        if response.status_code == 200:
            response_data = response.json()
            return response_data['id']
