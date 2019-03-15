import uuid
from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from activity_types.models import ActivityType
from walking_suggestion_times.models import SuggestionTime

class AbstractActivity(models.Model):
    class Meta:
        abstract = True

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    type = models.ForeignKey(ActivityType)
    vigorous = models.BooleanField(default=False)
    
    start = models.DateTimeField()
    date = models.DateField(null=True)
    timeOfDay = models.CharField(max_length=20, null=True, choices=SuggestionTime.CATEGORIES)
    duration = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def id(self):
        return str(self.uuid)

    def impute_start_datetime(self):
        suggestion_time = SuggestionTime.objects.get(
            user = self.user,
            category = self.timeOfDay
        )
        return suggestion_time.get_datetime_on(self.date)

class ActivityLog(AbstractActivity):
    enjoyed = models.FloatField(null=True, blank=True)

    @property
    def earned_minutes(self):
        if self.vigorous:
            return self.duration*2
        else:
            return self.duration

    def __str__(self):
        return "%s on %s (%s)" % (self.type, self.start, self.user)

class ActivityLogSource(models.Model):
    activity_log = models.OneToOneField(ActivityLog)
    user = models.ForeignKey(User, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey('content_type', 'object_id')

    updated_at = models.DateTimeField()

    @property
    def can_update(self):
        if self.updated_at == self.activity_log.updated_at:
            return True
        else:
            return False
