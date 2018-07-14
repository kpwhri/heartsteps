from django.db import models

from django.contrib.auth.models import User
from fcm_django.models import FCMDevice

from django.utils import timezone


class Message(models.Model):
    """
    A message sent from HeartSteps
    """

    reciepent = models.ForeignKey(User)
    device = models.ForeignKey(FCMDevice)

    title = models.CharField(max_length=100, blank=True, null=True)
    body = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    sent = models.DateTimeField(blank=True, null=True)
    recieved = models.DateTimeField(blank=True, null=True)

    def send(self):
        results = self.device.send_message(
            title = self.title,
            body = self.body
        )
        if(result['success']):
            self.sent = timezone.now()

    def markRecieved(self):
        self.recieved = timezone.now()