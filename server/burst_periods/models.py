from datetime import timedelta
from math import floor
from random import choice

from django.db import models
from django.contrib.auth import get_user_model

from daily_tasks.models import DailyTask

User = get_user_model()

class Configuration(models.Model):

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'    
    )
    enabled = models.BooleanField(default=True)

    period_length = models.PositiveIntegerField(default=7)
    interval_length = models.PositiveIntegerField(default=90)
    interval_variation = models.PositiveIntegerField(default=30)

    def generate_schedule(self, start, end):
        if not self.enabled:
            return None
        if start >= end:
            raise RuntimeError('Start date is greater than or equal to end date')
        last_possible_start = end - timedelta(days=self.period_length)
        if last_possible_start < start:
            raise RuntimeError('Last possible start is before start date')

        target_date = start + timedelta(days=self.interval_length)
        while target_date <= end:
            possible_start = target_date - timedelta(days=self.interval_variation)
            if possible_start < start:
                possible_start = start
            possible_end = target_date + timedelta(days=self.interval_variation)
            if possible_end + timedelta(days=self.period_length) > last_possible_start:
                possible_end = last_possible_start
            if possible_start < possible_end:
                possible_date_range = (possible_end - possible_start).days
                possible_dates = [possible_start + timedelta(days=offset) for offset in range(possible_date_range)]
                random_start = choice(possible_dates)
                BurstPeriod.objects.create(
                    user = self.user,
                    start = random_start,
                    end = random_start + timedelta(days=self.period_length)
                )
            target_date = target_date + timedelta(days=self.interval_length)
    

class BurstPeriod(models.Model):
    user = models.ForeignKey(User)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return '{start} to {end}'.format(
            start = self.start.strftime('%Y-%m-%d'),
            end = self.end.strftime('%Y-%m-%d')
        )
