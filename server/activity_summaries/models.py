import pytz
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth import get_user_model

from days.services import DayService
from activity_logs.models import ActivityLog
from fitbit_activities.services import FitbitDayService
from django.db.models import Sum

User = get_user_model()

class ActivitySummary(models.Model):
    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    
    activities_completed = models.PositiveIntegerField(default=0)
    miles = models.FloatField(default=0)
    minutes = models.PositiveIntegerField(default=0)
    steps = models.PositiveIntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'])
        ]

    def get_all_days(self):
        days = Day.objects.filter(user=self.user).order_by('updated').all()
        days_by_date = {}
        for day in days:
            days_by_date[day.date] = day
        return [days_by_date[_date] for _date in sorted(days_by_date.keys())]

    def update(self):
        days = self.get_all_days()
        # self.activities_completed = sum([_day.activities_completed for _day in days])
        # self.miles = sum([_day.miles for _day in days])
        # self.minutes = sum([_day.total_minutes for _day in days])
        # self.steps = sum([_day.steps for _day in days])
        self.activities_completed = Day.objects.filter(user=self.user).aggregate(Sum("activities_completed"))
        self.miles = Day.objects.filter(user=self.user).aggregate(Sum("miles"))
        self.minutes = Day.objects.filter(user=self.user).aggregate(Sum("total_minutes"))
        self.steps = Day.objects.filter(user=self.user).aggregate(Sum("steps"))
        self.save()

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

    @property
    def fitbit_day(self):
        if not hasattr(self, '_fitbit_day'):
            try:
                fitbitday_service = FitbitDayService(self.date, user=self.user)
                self._fitbit_day = fitbitday_service.day
            except FitbitDayService.NoAccount:
                self._fitbit_day = None
        return self._fitbit_day

    @property
    def wore_fitbit(self):
        if self.fitbit_day:
            return self.fitbit_day.wore_fitbit
        else:
            return False

    def update_from_fitbit(self):
        if self.fitbit_day:
            self.steps = self.fitbit_day.step_count
            self.miles = self.fitbit_day.distance
        else:
            self.steps = 0
            self.miles = 0
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
    
    def get_all_days_query(user, date):
        return Day.objects.filter(
            user = user,
            date = date
        ).order_by('updated')
    
    def get(user, date):
        return_day = Day.get_all_days_query(user, date).all().last()

        return return_day
