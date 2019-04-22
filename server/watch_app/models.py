from django.db import models
from django.contrib.auth.models import User

class WatchInstall(models.Model):
    user = models.ForeignKey(User)
    version = models.CharField(max_length=30, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class StepCount(models.Model):
    user = models.ForeignKey(User)
    step_number = models.CharField(max_length=1024, null=True)
    step_dtm = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-step_dtm']

    def __str__(self):
        return "%s steps %s @ %s" % (self.user, self.step_number, self.step_dtm)
