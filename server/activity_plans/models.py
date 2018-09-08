import uuid
from django.db import models
from django.contrib.auth.models import User

class ActivityType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)

    user = models.ForeignKey(User, null=True, blank=True)

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

class ActivityPlan(AbstractActivity):
    log = models.ForeignKey(ActivityLog, null=True, blank=True)

    def __str__(self):
        if self.log:
            verb = "completed on"
        else:
            verb = "planned for"
        return "%s %s %s (%s)" % (self.type, verb, self.start, self.user)
