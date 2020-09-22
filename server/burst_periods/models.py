from datetime import timedelta
from math import floor
from random import choice

from django.db import models
from django.contrib.auth import get_user_model

from daily_tasks.models import DailyTask

User = get_user_model()

class Configuration(models.Model):

    PERIOD_LENGTH_DAYS = 7
    DAYS_PER_PERIOD = 90
    BUFFER_PER_PERIOD = 60

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'    
    )
    enabled = models.BooleanField(default=True)

    def generate_schedule(self, start, end):
        if not self.enabled:
            return None
        if start >= end:
            raise RuntimeError('Start date is greater than or equal to end date')
        schedule_length = (end-start).days
        if schedule_length < self.DAYS_PER_PERIOD:
            raise RuntimeError('Not enough time for a period')
        number_of_periods = floor(schedule_length/self.DAYS_PER_PERIOD)
        periods = []
        for num in range(number_of_periods):
            period_start = start + timedelta(days=(num*self.DAYS_PER_PERIOD))
            period_end = period_start + timedelta(days=self.DAYS_PER_PERIOD)
            if period_end > end:
                period_end = end
            period_end = period_end - timedelta(days=self.PERIOD_LENGTH_DAYS)
            
            possible_dates = [period_start + timedelta(days=offset) for offset in range((period_end - period_start).days)]
            random_start = choice(possible_dates)
            BurstPeriod.objects.create(
                user = self.user,
                start = random_start,
                end = random_start + timedelta(days=self.PERIOD_LENGTH_DAYS)
            )

class BurstPeriod(models.Model):
    user = models.ForeignKey(User)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return '{start} to {end}'.format(
            start = self.start.strftime('%Y-%m-%d'),
            end = self.end.strftime('%Y-%m-%d')
        )
