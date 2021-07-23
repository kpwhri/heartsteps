from celery import shared_task
from datetime import datetime
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from .models import Message, MessageReceipt


@shared_task
def onesignal_get_received(message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return False
    message.update_message_receipts()
    if not message.received and (timezone.now() - message.created).seconds < 5 * 60:
        onesignal_get_received.apply_async(eta=5 * 60, kwargs={"message_id": message_id})
