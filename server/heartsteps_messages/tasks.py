# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Message


@shared_task
def send_message(message_id):
    message = Message.objects.get(id=message_id)
    if not message.sent:
        message.send()
        