from django.db import models
from django.contrib.auth.models import User

class ActivityType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=150)

    user = models.ForeignKey(User, null=True, blank=True)
