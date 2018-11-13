from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User


class StepCount(models.model):
    user = models.ForeignKey(User)
    payload = JSONField()
    step_count = models.IntegerField(null=True, blank=True)
    step_dtm = models.DateTimeField
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s @ %s" % (self.user, self.time)
