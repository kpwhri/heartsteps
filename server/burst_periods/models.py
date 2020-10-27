from datetime import timedelta
from math import floor
from random import choice

from django.db import models
from django.contrib.auth import get_user_model

from activity_surveys.models import Configuration as ActivitySurveyConfiguration
from daily_tasks.models import DailyTask
from days.services import DayService
from walking_suggestion_surveys.models import Configuration as WalkingSuggestionSurveyConfiguration

User = get_user_model()

class ConfigurationQuerySet(models.QuerySet):

    def prefetch_burst_periods(self):
        return self

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

    objects = ConfigurationQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.daily_task:
            self.daily_task = self.create_daily_task()
        super().save(*args, **kwargs)
        if self.enabled:
            self.daily_task.enable()
        else:
            self.daily_task.disable()

    @property
    def burst_periods(self):
        if not hasattr(self, '_burst_periods'):
            self._burst_periods = self.get_burst_periods()
        return self._burst_periods

    @property
    def current_burst_period(self):
        for burst_period in self.burst_periods:
            if burst_period.start <= self.current_date and burst_period.end >= self.current_date:
                return burst_period
        return None
    
    @property
    def previous_burst_periods(self):
        return [burst_period for burst_period in self.burst_periods if burst_period.end < self.current_date]

    @property
    def next_burst_periods(self):
        return [burst_period for burst_period in self.burst_periods if burst_period.start > self.current_date]

    @property
    def current_date(self):
        if not hasattr(self, '_current_date'):
            service = DayService(self.user)
            self._today = service.get_current_date()
        return self._today

    def set_current_intervention_configuration(self):
        self.update_intervention_configurations(
            date = self.current_date
        )

    def update_intervention_configurations(self, date):
        burst_period = BurstPeriod.objects.filter(
            user = self.user,
            start__lte = date,
            end__gte = date
        ).first()
        if burst_period:
            self.burst_intervention_configurations()
        else:
            self.normalize_intervention_configurations()

    def burst_intervention_configurations(self):
        self.burst_activity_surveys()
        self.burst_walking_suggestion_surveys()

    def normalize_intervention_configurations(self):
        self.normalize_activity_surveys()
        self.normalize_walking_suggestion_surveys()

    def burst_activity_surveys(self):
        self.update_activity_survey_probability(0.9)

    def normalize_activity_surveys(self):
        self.update_activity_survey_probability(0.2)

    def burst_walking_suggestion_surveys(self):
        self.update_walking_suggestion_survey_treatment_probability(0.9)

    def normalize_walking_suggestion_surveys(self):
        self.update_walking_suggestion_survey_treatment_probability(0.2)

    def update_activity_survey_probability(self, treatment_probability):
        try:
            configuration = ActivitySurveyConfiguration.objects.get(
                user = self.user
            )
            configuration.treatment_probability = treatment_probability
            configuration.save()
        except ActivitySurveyConfiguration.DoesNotExist:
            pass

    def update_walking_suggestion_survey_treatment_probability(self, treatment_probability):
        try:
            configuration = WalkingSuggestionSurveyConfiguration.objects.get(
                user = self.user
            )
            configuration.treatment_probability = treatment_probability
            configuration.save()
        except WalkingSuggestionSurveyConfiguration.DoesNotExist:
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

    def get_burst_periods(self):
        return BurstPeriod.objects.filter(
            user = self.user
        ).all()
    

class BurstPeriod(models.Model):
    user = models.ForeignKey(User)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        ordering = ['start', 'user']

    def __str__(self):
        return '{start} to {end}'.format(
            start = self.start.strftime('%Y-%m-%d'),
            end = self.end.strftime('%Y-%m-%d')
        )
