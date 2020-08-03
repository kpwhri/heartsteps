from django.db import models
from django.contrib.auth import get_user_model

from sms_messages.models import Message

User = get_user_model()

class Configuration(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = '+'
    )
    closeout_date = models.DateField()
    message = models.ForeignKey(
        Message,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    def __str__(self):
        return "{date} ({user_id})".format(
            user_id = self.user_id,
            date = self.closeout_date
        )
