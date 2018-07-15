import uuid
from django.db import models

from django.contrib.auth.models import User
from fcm_django.models import FCMDevice

from django.utils import timezone


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
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=255)

    context_tags = models.ManyToManyField(ContextTag)

    def __str__(self):
        return self.title

class Message(models.Model):
    """
    A message sent from HeartSteps
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    reciepent = models.ForeignKey(User)
    device = models.ForeignKey(FCMDevice, blank=True, null=True)

    message_template = models.ForeignKey(MessageTemplate, null=True, blank=True)

    title = models.CharField(max_length=100, blank=True, null=True)
    body = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    sent = models.DateTimeField(blank=True, null=True)
    recieved = models.DateTimeField(blank=True, null=True)

    def send(self):
        if not self.device:
            try:
                device = FCMDevice.objects.get(
                    user=self.reciepient,
                    active=True
                    )
                self.device = device
            except FCMDevice.DoesNotExist:
                return False
        
        results = self.device.send_message(
            title = self.title,
            body = self.body
        )
        self.sent = timezone.now()
        self.save()

        if(result['success']):
            return True
        return False

    def markRecieved(self):
        self.recieved = timezone.now()

    def __str__(self):
        if self.recieved:
            return "To %s (recieved)" % (self.reciepent)
        return "To %s" % (self.reciepent)