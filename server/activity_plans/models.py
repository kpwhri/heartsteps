from django.db import models
from activity_logs.models import AbstractActivity, ActivityLog

class ActivityPlan(AbstractActivity):
    complete = models.BooleanField(default=False)
    log = models.OneToOneField(ActivityLog, null=True, blank=True)

    def __str__(self):
        if self.log:
            verb = "completed on"
        else:
            verb = "planned for"
        return "%s %s %s (%s)" % (self.type, verb, self.start, self.user)
