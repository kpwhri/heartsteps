import requests
import json
from datetime import datetime

# from apns2.client import APNsClient
# from apns2.payload import Payload

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
# from .models import OneSignalInfo
import push_messages
from user_event_logs.models import EventLog

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'

class ClientBase:

    SENT = 'sent'
    RECEIVED = 'received'
    FAILED = 'failed'

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

    SENT = 'onesignal-sent'

    def __init__(self, device):
        self.device = device
        self.user = device.user

    def get_one_signal_notification_url(self):
        EventLog.debug(self.user)
        return 'https://onesignal.com/api/v1/notifications'

    def get_api_key(self):
        (id, key) = push_messages.models.OneSignalInfo.get(user=self.user)
        
        return key
        # if not hasattr(settings, 'ONESIGNAL_API_KEY'):
        #     raise ImproperlyConfigured('No OneSignal API KEY')
        # return settings.ONESIGNAL_API_KEY

    def get_app_id(self):
        (id, key) = push_messages.models.OneSignalInfo.get(user=self.user)
        
        return id
        # if not hasattr(settings, 'ONESIGNAL_APP_ID'):
        #     raise ImproperlyConfigured('No OneSignal APP ID')
        # return settings.ONESIGNAL_APP_ID

    def get_message_receipts(self, message_id):
            url = 'https://onesignal.com/api/v1/notifications/{message_id}?app_id={app_id}'.format(
                app_id = self.get_app_id(),
                message_id = message_id
            )
            response = requests.get(url, headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % (self.get_api_key())
            })
            if response.status_code == 200:
                data = response.json()
                receipts = {}
                if 'send_after' in data and data['send_after']:
                    receipts[self.SENT] = timezone.make_aware(datetime.fromtimestamp(data['send_after']))
                if 'completed_at' in data and data['completed_at']:
                    completed_datetime = timezone.make_aware(datetime.fromtimestamp(data['completed_at']))
                    if 'successful' in data and data['successful'] > 0:
                        receipts[self.RECEIVED] = completed_datetime
                    else:
                        receipts[self.FAILED] = completed_datetime
                return receipts
            else:
                raise RuntimeError('OneSignal message status request failed')

    def send(self, body=None, title=None, collapse_subject=None, data={}):
        EventLog.debug(self.user)
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
        EventLog.debug(self.user)
        if response.status_code == 200:
            import pprint
            EventLog.debug(self.user, pprint.pformat(response.__dict__))
            response_data = response.json()
            EventLog.debug(self.user, pprint.pformat(response_data))
            if 'errors' in response_data and response_data['errors'] and len(response_data['errors']) > 0:
                EventLog.debug(self.user, response_data['errors'][0])
                raise self.MessageSendError(response_data['errors'][0])
            return response_data['id']
        else:
            EventLog.debug(self.user)
            raise self.MessageSendError(response.text)
