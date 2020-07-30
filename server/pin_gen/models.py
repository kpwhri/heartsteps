from random import choice
import uuid

from django.db import models
from django.contrib.auth.models import User

class Pin(models.Model):

    pin_digits = models.IntegerField(null=True)
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return str(self.pin_digits)

class ClockFacePin(models.Model):
    pin = models.CharField(
        max_length = 10,
        unique = True
    )

    uniid = models.CharField(
        max_length = 50,
        null = True,
        unique = True
    )

    user = models.ForeignKey(
        User,
        null = True,
        on_delete = models.SET_NULL
    )

    def get_unique_pin(self):
        pin_choices = [str(_i) for _i in [0,1,2,3,4,5,6,7,8,9]]
        pin = ''.join([choice(pin_choices) for _ in range(5)])
        exists = ClockFacePin.objects.filter(pin = pin).count()
        if exists:
            return self.get_unique_pin()
        else:
            return pin

    def get_unique_uniid(self):
        temp = str(uuid.uuid4())
        exists = ClockFacePin.objects.filter(uniid = temp).count()
        if exists:
            return self.get_unique_uniid
        else:
            return temp

    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = self.get_unique_pin()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.pin
