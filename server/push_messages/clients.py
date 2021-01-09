import requests
import json
from datetime import datetime

# from apns2.client import APNsClient
# from apns2.payload import Payload

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from .tasks import onesignal_get_received

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'

class ClientBase:

    class MessageSendError(RuntimeError):
        pass

    def __init__(self, device):
        self.device = device

    def send(self, body=None, title=None, collapse_subject=None, data=None):
        return None
    

class ApplePushClient(ClientBase):

    def get_client(self):
        pass
        # return APNsClient('/credentials/heartsteps-apns.pem')

    def send(self, request):
        pass
        # payload = Payload(
        #     content_available=True,
        #     custom=request
        # )
        # client = self.get_client()
        # client.send_notification(self.device.token, payload, 'com.nickreid.heartsteps.voip')

class AppleDevelopmentPushClient(ApplePushClient):

    def get_client(self):
        pass
        # return APNsClient('/credentials/heartsteps-apns.pem', use_sandbox=True)

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

class OneSignalClient(ClientBase):

    def __init__(self, device):
        self.device = device

    def get_one_signal_notification_url(self):
        return 'https://onesignal.com/api/v1/notifications'

    def get_api_key(self):
        if not hasattr(settings, 'ONESIGNAL_API_KEY'):
            raise ImproperlyConfigured('No OneSignal API KEY')
        return settings.ONESIGNAL_API_KEY

    def get_app_id(self):
        if not hasattr(settings, 'ONESIGNAL_APP_ID'):
            raise ImproperlyConfigured('No OneSignal APP ID')
        return settings.ONESIGNAL_APP_ID

    def send(self, body=None, title=None, collapse_subject=None, data={}):
        
        response = requests.post(
            self.get_one_signal_notification_url(),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % (self.get_api_key())
            },
            json = {
                'app_id': self.get_app_id(),
                'include_player_ids': [self.device.token],
                'contents': {
                    'en': body
                },
                'headings': {
                    'en': title
                },
                'collapse_id': collapse_subject,
                'data': data
            }
        )

        if response.status_code == 200:
            response_data = response.json()
            if 'errors' in response_data and response_data['errors'] and len(response_data['errors']) > 0:
                raise self.MessageSendError(response_data['errors'][0])
            message_id = response_data['id']
            onesignal_get_received.apply_async(countdown=300, kwargs={
                'message_id': message_id
            })
            return message_id
        else:
            raise self.MessageSendError(response.text)
