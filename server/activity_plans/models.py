import uuid

from django.db import models
from django.contrib.auth.models import User

from activity_types.models import ActivityType

class ActivityPlan(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    type = models.ForeignKey(ActivityType)
    vigorous = models.BooleanField(default=False)
    
    start = models.DateTimeField()
    duration = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    complete = models.BooleanField(default=False)
    enjoyed = models.IntegerField(null=True, blank=True)

    @property
    def id(self):
        return str(self.uuid)

    def __str__(self):
        if self.log:
            verb = "completed on"
        else:
            verb = "planned for"
        return "%s %s %s (%s)" % (self.type, verb, self.start, self.user)
