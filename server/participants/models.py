from django.db import models
from django.contrib.auth.models import User


class Participant(models.Model):
    user = models.ForeignKey(User)
    enrollment_token = models.CharField(max_length=10)
