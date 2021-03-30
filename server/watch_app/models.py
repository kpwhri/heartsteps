from django.db import models
from django.contrib.auth.models import User

class WatchInstall(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    version = models.CharField(max_length=30, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class StepCount(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    steps = models.PositiveSmallIntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start']

    def __str__(self):
        return "%s steps %d @ %s" % (self.user, self.steps, self.end)
