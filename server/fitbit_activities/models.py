import uuid, pytz, math
from datetime import datetime, timedelta

from django.db import models
from django.contrib.postgres.fields import JSONField

from fitbit_api.models import FitbitAccount

class FitbitActivityType(models.Model):
    fitbit_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class FitbitActivity(models.Model):
    account = models.ForeignKey(FitbitAccount)
    fitbit_id = models.CharField(max_length=50)

    type = models.ForeignKey(FitbitActivityType, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    average_heart_rate = models.IntegerField(null=True)

    payload = JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        unique_together = [('account', 'fitbit_id')]

    @property
    def duration(self):
        if self.start_time and self.end_time:
            difference = self.end_time - self.start_time
            return math.ceil(difference.seconds/60)
        else:
            return 0

class FitbitDay(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(FitbitAccount)
    date = models.DateField()
    _timezone = models.CharField(max_length=50, default=pytz.UTC.zone)

    step_count = models.PositiveIntegerField(default=0)
    _distance = models.DecimalField(default=0, max_digits=9, decimal_places=3)
    average_heart_rate = models.PositiveIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        unique_together = ('account', 'date')

    @property
    def timezone(self):
        return self.get_timezone()

    @property
    def distance(self):
        return float(self._distance)
    
    @distance.setter
    def distance(self, value):
        self._distance = value

    def get_timezone(self):
        return pytz.timezone(self._timezone)
    
    def get_start_datetime(self):
        timezone = self.get_timezone()
        return timezone.localize(datetime(
            year = self.date.year,
            month = self.date.month,
            day = self.date.day,
            hour = 0,
            minute = 0
        ))

    def get_end_datetime(self):
        start_time = self.get_start_datetime()
        return start_time + timedelta(days=1)

    @property
    def activities(self):
        activities = FitbitActivity.objects.filter(
            account = self.account,
            start_time__range = [self.get_start_datetime(), self.get_end_datetime()]
        )
        return list(activities)

    def __str__(self):
        return "%s: %s" % (self.account, self.date.strftime('%Y-%m-%d'))

class FitbitMinuteStepCount(models.Model):
    account = models.ForeignKey(FitbitAccount)
    time = models.DateTimeField()
    steps = models.IntegerField()

class FitbitDailyUnprocessedData(models.Model):
    account = models.ForeignKey(FitbitAccount)
    day = models.ForeignKey(FitbitDay)
    category = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50, null=True, blank=True)

    payload = JSONField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('day', 'category')

