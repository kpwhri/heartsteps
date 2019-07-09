from django.contrib.auth import get_user_model
from django.db import models

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
