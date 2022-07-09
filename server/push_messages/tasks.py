from celery import shared_task
from datetime import datetime, timedelta
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from .models import Message, MessageReceipt


def onesignal_refresh_interval():
    if not hasattr(settings, 'ONESIGNAL_REFRESH_INTERVAL'):
        # TODO: remove print, for debugging
        print('ONESIGNAL REFRESH INTERVAL NOT CONFIGURED')
        raise ImproperlyConfigured("No ONESIGNAL_REFRESH_INTERVAL")
    return settings.ONESIGNAL_REFRESH_INTERVAL


@shared_task
def onesignal_get_received(message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return False
    message.update_message_receipts()
    if not message.received and (timezone.now() - message.created).seconds < 5 * 60:
        onesignal_get_received.apply_async(
            eta=datetime.now() + timedelta(seconds=onesignal_refresh_interval()), kwargs={"message_id": message_id})
