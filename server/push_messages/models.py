import json
import uuid
from django.db import models

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    token = models.CharField(max_length=255)
    type = models.CharField(max_length=10, null=True, blank=True)

    active = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s (%s)' % (self.type, self.token)

class Message(models.Model):

    DATA = 'data'
    NOTIFICATION = 'notification'
    MESSAGE_TYPES = [
        (DATA, 'Data'),
        (NOTIFICATION, 'Notification')
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)

    recipient = models.ForeignKey(User)
    device = models.ForeignKey(Device, null=True)

    data = JSONField(null=True)
    content = models.TextField(null=True)
    title = models.TextField(max_length=150, null=True)
    body = models.TextField(max_length=355, null=True)
    collapse_subject = models.CharField(max_length=150, null=True)

    external_id = models.CharField(max_length=150, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s (%s)' % (self.recipient.username, self.message_type)

    def __get_receipt_time(self, type):
        try:
            receipt = MessageReceipt.objects.filter(message=self, type=type).last()
            return receipt.time
        except:
            return None

    @property
    def sent(self):
        return self.__get_receipt_time(MessageReceipt.SENT)

    @property
    def received(self):
        return self.__get_receipt_time(MessageReceipt.RECEIVED)

    @property
    def displayed(self):
        return self.__get_receipt_time(MessageReceipt.DISPLAYED)
    
    @property
    def opened(self):
        return self.__get_receipt_time(MessageReceipt.OPENED)

    @property
    def engaged(self):
        return self.__get_receipt_time(MessageReceipt.ENGAGED)

class MessageReceipt(models.Model):
    SENT = 'sent'
    RECEIVED = 'received'
    DISPLAYED = 'displayed'
    OPENED = 'opened'
    ENGAGED = 'engaged'


    MESSAGE_RECEIPT_TYPES = [SENT, RECEIVED, DISPLAYED, OPENED, ENGAGED]

    MESSAGE_RECEIPT_CHOICES = (
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
        (DISPLAYED, 'Displayed'),
        (OPENED, 'Opened'),
        (ENGAGED, 'Engaged')
    )

    message = models.ForeignKey(Message)
    time = models.DateTimeField()
    type = models.CharField(max_length=20, choices=MESSAGE_RECEIPT_CHOICES)