import uuid

from django.db import models
from django.contrib.auth.models import User

from activity_types.models import ActivityType

class AbstractActivity(models.Model):
    class Meta:
        abstract = True

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    type = models.ForeignKey(ActivityType)
    vigorous = models.BooleanField(default=False)
    
    start = models.DateTimeField()
    duration = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ActivityLog(AbstractActivity):
    enjoyed = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "%s on %s (%s)" % (self.type, self.start, self.user)
