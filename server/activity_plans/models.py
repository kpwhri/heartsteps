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
        if self.activity_log and self.activity_log.id:
            return True
        else:
            return False

    def update_activity_log(self):
        activity_log = self.activity_log
        if not activity_log:
            activity_log = ActivityLog(
                user = self.user,
            )
        activity_log.type = self.type
        activity_log.date = self.date
        activity_log.start = self.start
        activity_log.timeOfDay = self.timeOfDay
        activity_log.duration = self.duration
        activity_log.vigorous = self.vigorous
        activity_log.save()

        if not self.activity_log:
            self.activity_log = activity_log
            self.save()

    def remove_activity_log(self):
        if self.activity_log:
            self.activity_log.delete()
            self.activity_log = None
            self.save()

    def __str__(self):
        if self.complete:
            verb = "completed on"
        else:
            verb = "planned for"
        return "%s %s %s (%s)" % (self.type, verb, self.start, self.user)
