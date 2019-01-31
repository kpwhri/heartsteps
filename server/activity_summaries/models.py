import pytz
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth import get_user_model

from locations.services import LocationService
from activity_logs.models import ActivityLog
from fitbit_api.models import FitbitMinuteStepCount
from fitbit_api.services import FitbitService

User = get_user_model()

class Day(models.Model):

    user = models.ForeignKey(User)
    date = models.DateField()
    steps = models.PositiveIntegerField(default=0)
    miles = models.FloatField(default=0)

    moderate_minutes = models.PositiveIntegerField(default=0)
    vigorous_minutes = models.PositiveIntegerField(default=0)
    total_minutes = models.PositiveIntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)

    @property
    def timezone(self):
        if hasattr(self, '__timezone'):
            return self.__timezone
        try:
            location_service = LocationService(user=self.user)
            self.__timezone = location_service.get_timezone_on(self.date)
        except LocationService.UnknownLocation:
            self.__timezone = pytz.UTC
        return self.__timezone

    @property
    def day_start(self):
        return self.timezone.localize(
            datetime(self.date.year, self.date.month, self.date.day)
        )

    @property
    def day_end(self):
        return self.day_start + timedelta(days=1)

    def update_from_fitbit(self):
        try:
            account = FitbitService.get_account(self.user)
        except FitbitService.NoAccount:
            return False
        step_counts = FitbitMinuteStepCount.objects.filter(
            account = account,
            time__range = [
                self.day_start,
                self.day_end
            ]
        ).all()
        self.steps = 0
        for step_count in step_counts:
            self.steps += step_count.steps
        self.save()
    
    def update_from_activities(self):
        self.moderate_minutes = 0
        self.vigorous_minutes = 0
        self.total_minutes = 0

        activities = ActivityLog.objects.filter(
            user = self.user,
            start__gte = self.day_start,
            start__lte = self.day_end
        ).all()
        for activity in activities:
            self.total_minutes += activity.earned_minutes
            if activity.vigorous:
                self.vigorous_minutes += activity.duration
            else:
                self.moderate_minutes += activity.duration
        self.save()