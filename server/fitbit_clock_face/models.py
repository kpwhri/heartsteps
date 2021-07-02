from random import choice
import uuid

from django.db import models
from django.contrib.auth.models import User

class ClockFace(models.Model):
    pin = models.CharField(
        max_length = 10,
        unique = True
    )
    token = models.CharField(
        max_length = 50,
        unique = True,
        default = uuid.uuid4
    )
    user = models.ForeignKey(
        User,
        null = True,
        on_delete = models.SET_NULL
    )

    created = models.DateTimeField(auto_now_add=True)

    @property
    def paired(self):
        if self.user_id:
            return True
        else:
            return False

    @property
    def username(self):
        if self.user:
            return self.user.username
        else:
            return None

    def get_unique_pin(self):
        pin_choices = [str(_i) for _i in [0,1,2,3,4,5,6,7,8,9]]
        pin = ''.join([choice(pin_choices) for _ in range(5)])
        exists = ClockFace.objects.filter(pin = pin).count()
        if exists:
            return self.get_unique_pin()
        else:
            return pin

    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = self.get_unique_pin()
        super().save(*args, **kwargs)


class ClockFaceStepCount(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )
    steps = models.PositiveIntegerField()
    time = models.DateTimeField()
