from datetime import timedelta
from math import floor
from random import choice

from django.db import models
from django.contrib.auth import get_user_model

from activity_surveys.models import Configuration as ActivitySurveyConfiguration
from daily_tasks.models import DailyTask
from walking_suggestion_surveys.models import Configuration as WalkingSuggestionSurveyConfiguration

User = get_user_model()

class Configuration(models.Model):

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'    
    )
    enabled = models.BooleanField(default=True)

    daily_task = models.ForeignKey(
        DailyTask,
        null = True,
        related_name = '+',
        on_delete = models.SET_NULL
    )

    period_length = models.PositiveIntegerField(default=7)
    interval_length = models.PositiveIntegerField(default=90)
    interval_variation = models.PositiveIntegerField(default=30)

    def save(self, *args, **kwargs):
        if not self.daily_task:
            self.daily_task = self.create_daily_task()
        super().save(*args, **kwargs)
        if self.enabled:
            self.daily_task.enable()
        else:
            self.daily_task.disable()

    def update_randomization_probabilities(self, date):
        pass

    def enable_burst_probabilities(self):
        pass

    def disable_burst_probabilities(self):
        pass

    def create_daily_task(self):
        daily_task = DailyTask.create_daily_task(
            user = self.user,
            category = None,
            task = 'burst_periods.tasks.update_burst_probability',
            name = 'Burst probability update for %s' % (self.user.username),
            arguments = {
                'username': self.user.username
            },
            hour = 3,
            minute = 0
        )
        return daily_task

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
