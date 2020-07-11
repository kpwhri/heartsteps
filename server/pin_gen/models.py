from django.db import models
from django.contrib.auth.models import User


class Pin(models.Model):
    pin_digits = models.IntegerField(null=True)
    user = models.ForeignKey(User)

    def __str__(self):
        return self.pin_digits


