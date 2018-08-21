import requests
import json
import uuid
from django.conf import settings

from push_messages.models import Device, Message

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'

def get_device_for_user(user):
    try:
        device = Device.objects.get(user=user, active=True)
    except Device.DoesNotExist:
        raise ValueError('User does not have active device')
    
    return device

def make_headers():
    if not settings.FCM_SERVER_KEY:
        raise ValueError('FCM SERVER KEY not set')

    return {
        'Authorization': 'key=%s' % settings.FCM_SERVER_KEY,
        'Content-Type': 'application/json'
    }

def send(user, request):
    headers = make_headers()

    device = get_device_for_user(user)
    request['to'] = device.token
    request['priority'] = 'high'

    message_id = uuid.uuid4()
    request['data']['messageId'] = str(message_id)

    message = Message.objects.create(
        id = message_id,
        recipient = user,
        device = device,
        content = json.dumps(request)
    )

    response = requests.post(
        FCM_SEND_URL,
        headers = headers,
        json = request
    )
    return message


def send_notification(user, title, body, data={}):
    request = {
        'notification': {
            'title': title,
            'body': body
        },
        'data': data
    }
    return send(user, request)

def send_data(user, data):
    request = {
        'content_available': True,
        'data': data
    }
    return send(user, request)