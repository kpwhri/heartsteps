import uuid
from django.db import models

from django.contrib.auth.models import User

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    token = models.CharField(max_length=255)
    type = models.CharField(max_length=10, null=True, blank=True)

    active = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=50, null=True, blank=True)

    recipient = models.ForeignKey(User)
    device = models.ForeignKey(Device, null=True)

    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)

class MessageReceipt(models.Model):
    SENT = 'sent'
    RECEIVED = 'received'
    OPENED = 'opened'
    ENGAGED = 'engaged'

    MESSAGE_RECIEPT_TYPES = (
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
        (OPENED, 'Opened'),
        (ENGAGED, 'Engaged')
    )


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message)
    
    time = models.DateTimeField()
    type = models.CharField(max_length=20, choices=MESSAGE_RECIEPT_TYPES)