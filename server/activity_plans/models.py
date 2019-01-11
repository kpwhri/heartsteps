import uuid

from django.db import models
from django.contrib.auth.models import User

from activity_logs.models import AbstractActivity, ActivityLog, ActivityType

class ActivityPlan(AbstractActivity):

    activity_log = models.OneToOneField(ActivityLog, null=True, on_delete=models.SET_NULL)

    @property
    def id(self):
        return str(self.uuid)

    @property
    def complete(self):
        if self.activity_log:
            return True
        else:
            return False

    def update_activity_log(self):
        if not self.activity_log:
            self.activity_log = ActivityLog.objects.create(
                user = self.user,
                type = self.type,
                start = self.start,
                duration = self.duration,
            )
            self.save()
        self.activity_log.type = self.type
        self.activity_log.start = self.start
        self.activity_log.duration = self.duration
        self.activity_log.vigorous = self.vigorous
        self.activity_log.save()

    def remove_activity_log(self):
        if self.activity_log:
            self.activity_log.delete()

    def __str__(self):
        if self.complete:
            verb = "completed on"
        else:
            verb = "planned for"
        return "%s %s %s (%s)" % (self.type, verb, self.start, self.user)
