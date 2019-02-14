import requests
import json

from apns2.client import APNsClient
from apns2.payload import Payload

from django.conf import settings

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'
ONESIGNAL_SEND_URL = 'https://onesignal.com/api/v1/notifications'

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
        return APNsClient('/credentials/heartsteps-aps-production.pem')

    def send(self, request):
        payload = Payload(
            content_available=True,
            custom=request
        )
        client = self.get_client()
        client.send_notification(self.device.token, payload, 'com.nickreid.heartsteps')

class AppleDevelopmentPushClient(ApplePushClient):

    def get_client(self):
        return APNsClient('/credentials/heartsteps-aps-development.pem', use_sandbox=True)

class OnesignalMessageService(ClientBase):
    """
    Sends Push Notifications to OneSignal
    """

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

