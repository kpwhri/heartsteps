from django.db import models
from django.contrib.auth.models import User

class ActivityType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=150)

    user = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        suffix = ''
        if self.user:
            suffix = '(%s)' % (self.user.username)
        if self.title:
            return '%s %s' % (self.title, suffix)
        else:
            return '%s %s' % (self.name, suffix)
