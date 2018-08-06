import uuid
import requests
from django.db import models
from django.utils import timezone
from django.conf import settings

from django.contrib.auth.models import User

FCM_SEND_URL = 'https://fcm.googleapis.com/fcm/send'

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    token = models.CharField(max_length=255)
    type = models.CharField(max_length=10, null=True, blank=True)

    active = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    def send(self, request):
        if not settings.FCM_SERVER_KEY:
            raise ValueError('FCM SERVER KEY not set')

        headers = {
            'Authorization': 'key=%s' % settings.FCM_SERVER_KEY,
            'Content-Type': 'application/json'
        }

        request['to'] = self.token
        request['collapse_key'] = 'type_a'

        requests.post(
            FCM_SEND_URL,
            headers = headers,
            json = request
        )

    def send_notification(self, title, body, data={}):
        fcm_request = {
            'notification': {
                'title': title,
                'body': body
            },
            'data': data
        }
        self.send(fcm_request)

    def send_data(self, data):
        fcm_request = {
            'content_available': True,
            'data': data
        }
        self.send(fcm_request)

class ContextTag(models.Model):
    """
    Used to organize and filter message templates
    """
    tag = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.tag

class MessageTemplate(models.Model):
    """
    Message templates used to populate messages that are sent to users
    """
    title = models.CharField(max_length=100, null=True, blank=True)
    body = models.CharField(max_length=255)

    context_tags = models.ManyToManyField(ContextTag)

    def __str__(self):
        return self.body

class Message(models.Model):
    """
    A message sent from HeartSteps
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    reciepent = models.ForeignKey(User)
    device = models.ForeignKey(Device, null=True)

    message_template = models.ForeignKey(MessageTemplate, null=True, blank=True)

    title = models.CharField(max_length=100, blank=True, null=True)
    body = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    sent = models.DateTimeField(blank=True, null=True)
    recieved = models.DateTimeField(blank=True, null=True)

    def send(self):
        if not self.device:
            try:
                device = Device.objects.get(user=self.reciepent, active=True)
            except Device.DoesNotExist:
                return False
            self.device = device
        
        self.device.send_notification(self.title, self.body)

        self.sent = timezone.now()
        self.save()

        return True

    def markRecieved(self):
        self.recieved = timezone.now()

    def __str__(self):
        if self.recieved:
            return "To %s (recieved)" % (self.reciepent)
        return "To %s" % (self.reciepent)