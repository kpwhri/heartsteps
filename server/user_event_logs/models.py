from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models


User = get_user_model()


class EventLog(models.Model):

    SUCCSESS = 'success'
    ERROR = 'error'

    user = models.ForeignKey(
        User,
        null = True,
        related_name = '+',
        on_delete = models.CASCADE
    )
    status = models.CharField(max_length=25)

    message = models.CharField(max_length=250, null=True)
    data = JSONField(null=True)
