import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from days.services import DayService
from fitbit_activities.models import FitbitActivity
from surveys.models import Question
from surveys.models import Survey

User = get_user_model()

class Configuration(models.Model):
    user = models.OneToOneField(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    enabled = models.BooleanField(default = True)
    treatment_probability = models.FloatField(null=True)

    @property
    def last_decision(self):
        if not hasattr(self, '_last_decision'):
            self._last_decision = self.get_last_decision()
        return self._last_decision

    @property
    def last_survey(self):
        if not hasattr(self, '_last_survey'):
            self._last_survey = self.get_last_survey()
        return self._last_survey

    @property
    def last_answered_survey(self):
        if not hasattr(self, '_last_answered_survey'):
            self._last_answered_survey = self.get_last_answered_survey()
        return self._last_answered_survey

    def get_last_decision(self):
        last_decision = Decision.objects.filter(
            user = self.user
        ) \
        .order_by('created') \
        .last()
        if not last_decision:
            return None
        day_service = DayService(user = self.user)
        tz = day_service.get_timezone_at(last_decision.created)
        last_decision.created = last_decision.created.astimezone(tz)
        return last_decision

    def get_last_survey(self):
        activity_survey = ActivitySurvey.objects.filter(
            user = self.user
        ).order_by('created') \
        .last()
        return activity_survey

    def get_last_answered_survey(self):
        activity_survey = ActivitySurvey.objects.filter(
            user = self.user,
            answered = True
        ).order_by('created') \
        .last()
        return activity_survey

class Decision(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    treated = models.BooleanField()
    treatment_probability = models.FloatField()

    fitbit_activity = models.ForeignKey(
        FitbitActivity,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
    activity_survey = models.ForeignKey(
        'activity_surveys.ActivitySurvey',
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if 'treatment_probability' in kwargs:
            self.treatment_probability = kwargs['treatment_probability']
        if 'treated' in kwargs:
            self.treated = kwargs['treated']
        if self.treated is None:
            self.randomize()
        super().save(*args, **kwargs)
        

    def randomize(self, treatment_probability=None):
        if treatment_probability is not None:
            self.treatment_probability = treatment_probability
        if self.treatment_probability is None:
            self.treatment_probability = self.get_default_probability()
        if random.random() < self.treatment_probability:
            self.treated = True
        else:
            self.treated = False
        
    def get_default_probability(self):
        if hasattr(settings, 'ACTIVITY_SURVEY_DEFAULT_PROBABILITY'):
            return settings.ACTIVITY_SURVEY_DEFAULT_PROBABILITY
        raise ImproperlyConfigured('No default activity survey decision probability')

class ActivitySurveyQuestion(Question):
    pass

class ActivitySurvey(Survey):
    
    QUESTION_MODEL = ActivitySurveyQuestion

    decision = models.ForeignKey(
        Decision,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
    fitbit_activity = models.ForeignKey(
        FitbitActivity,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

