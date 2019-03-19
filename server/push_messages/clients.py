import requests
import json

from apns2.client import APNsClient
from apns2.payload import Payload

from django.conf import settings

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

