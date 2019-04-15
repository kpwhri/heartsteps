from celery import shared_task
from datetime import datetime
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from push_messages.models import Message, MessageReceipt

@shared_task
def onesignal_get_received(message_id):
    try:
        message = Message.objects.get(external_id=message_id)
    except Message.DoesNotExist:
        return False

    if not settings.ONESIGNAL_API_KEY:
        raise ImproperlyConfigured('No OneSignal API KEY')
    if not settings.ONESIGNAL_APP_ID:
        raise ImproperlyConfigured('No OneSignal APP ID')
    api_key = settings.ONESIGNAL_API_KEY
    app_id = settings.ONESIGNAL_APP_ID

    url = 'https://onesignal.com/api/v1/notifications/%s?app_id=%s' % (message_id, app_id)
    response = requests.get(url, headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic %s' % (api_key)
    })

    if response.status_code == 200:
        data = response.json()
        timestamp = data['completed_at']
        received_time = timezone.make_aware(datetime.fromtimestamp(timestamp))
        
        MessageReceipt.objects.create(
            message=message,
            time=received_time,
            type=MessageReceipt.RECEIVED
        )
    else:
        raise RuntimeError('Request failed')
