from django.contrib.auth import get_user_model
from django.db import models

import participants

User = get_user_model()

class Contact(models.Model):
    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    enabled = models.BooleanField(
        default = True
    )
    number = models.CharField(max_length=30)

    @property
    def messages(self):
        messages = Message.objects.filter(
            models.Q(recipient=self.number) | models.Q(sender=self.number)
        ).all()
        return list(messages)

class Message(models.Model):
    recipient = models.CharField(max_length=30)
    sender = models.CharField(max_length=30)
    body = models.TextField(
        null = True
    )
    external_id = models.CharField(
        max_length=34,
        null=True
    )

    created = models.DateTimeField(auto_now_add=True)

class TwilioAccountInfo(models.Model):
    account_sid = models.CharField(max_length=200, null=True)
    auth_token = models.CharField(max_length=200, null=True)
    from_phone_number = models.CharField(max_length=200, null=True)
    study = models.OneToOneField(participants.models.Study, blank=True, null=True, on_delete=models.SET_NULL)