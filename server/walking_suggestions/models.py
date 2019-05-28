import pytz
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from behavioral_messages.models import MessageTemplate
from days.services import DayService
from randomization.models import Decision
from service_requests.models import ServiceRequest
from walking_suggestion_times.models import SuggestionTime

class Configuration(models.Model):
    user = models.ForeignKey(User)
    enabled = models.BooleanField(default=False)

    service_initialized_date = models.DateField(null=True)
    pooling = models.BooleanField(default=False)

    day_start_hour = models.PositiveSmallIntegerField(default=6)
    day_start_minute = models.PositiveSmallIntegerField(default=0)
    day_end_hour = models.PositiveSmallIntegerField(default=21)
    day_end_minute = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.user.username
    
    @property
    def service_initialized(self):
        if self.service_initialized_date is not None:
            return True
        else:
            return False

    @property
    def timezone(self):
        service = DayService(user=self.user)
        return service.get_current_timezone()

    @property
    def current_datetime(self):
        return timezone.now().astimezone(self.timezone)

    def get_start_of_day(self, day=None):
        if not day:
            day = self.current_datetime
        return datetime(
            year = day.year,
            month = day.month,
            day = day.day,
            hour = self.day_start_hour,
            minute = self.day_start_minute,
            tzinfo = self.timezone
        )

    def get_end_of_day(self, day=None):
        if not day:
            day = self.current_datetime
        return datetime(
            year = day.year,
            month = day.month,
            day = day.day,
            hour = self.day_end_hour,
            minute = self.day_end_minute,
            tzinfo = self.timezone
        )

    @property
    def suggestion_times(self):
        results = SuggestionTime.objects.filter(user=self.user).all()
        return list(results)

class WalkingSuggestionMessageTemplate(MessageTemplate):
    pass

class WalkingSuggestionServiceRequest(ServiceRequest):
    pass

class WalkingSuggestionDecision(Decision):

    MESSAGE_TEMPLATE_MODEL = WalkingSuggestionMessageTemplate
    
    @property
    def category(self):
        for tag in self.tags.all():
            if tag.tag in SuggestionTime.TIMES:
                return tag.tag
        return None

class NightlyUpdate(models.Model):
    user = models.ForeignKey(User)
    day = models.DateField()
    updated = models.BooleanField(default=False)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day']
