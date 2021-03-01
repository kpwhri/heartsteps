import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

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

class Decision(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    treated = models.BooleanField()
    treatment_probability = models.FloatField()

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

