import pytz
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth import get_user_model

from days.services import DayService
from activity_logs.models import ActivityLog
from fitbit_activities.services import FitbitDayService

User = get_user_model()

class Day(models.Model):

    user = models.ForeignKey(
        User,
        related_name='+',
        on_delete=models.CASCADE    
    )
    date = models.DateField()
    steps = models.PositiveIntegerField(default=0)
    miles = models.FloatField(default=0)

    activities_completed = models.PositiveIntegerField(default=0)
    moderate_minutes = models.PositiveIntegerField(default=0)
    vigorous_minutes = models.PositiveIntegerField(default=0)
    total_minutes = models.PositiveIntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s: %s' % (self.user.username, self.date.strftime('%Y-%m-%d'))

    @property
    def timezone(self):
        if hasattr(self, '__timezone'):
            return self.__timezone
        service = DayService(user=self.user)
        self.__timezone = service.get_timezone_at(self.date)
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
            fitbitday_service = FitbitDayService(self.date, user=self.user)
            fitbit_day = fitbitday_service.day
        except FitbitDayService.NoAccount:
            return False
        self.steps = fitbit_day.step_count
        self.miles = fitbit_day.distance
        self.save()
    
    def update_from_activities(self):
        self.activities_completed = 0
        self.moderate_minutes = 0
        self.vigorous_minutes = 0
        self.total_minutes = 0

        activities = ActivityLog.objects.filter(
            user = self.user,
            start__gte = self.day_start,
            start__lte = self.day_end
        ).all()
        for activity in activities:
            self.activities_completed += 1
            self.total_minutes += activity.earned_minutes
            if activity.vigorous:
                self.vigorous_minutes += activity.duration
            else:
                self.moderate_minutes += activity.duration
        self.save()