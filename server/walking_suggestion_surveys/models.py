from django.db import models

import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from surveys.models import Question
from surveys.models import Survey
from walking_suggestion_times.models import SuggestionTime

User = get_user_model()

class Configuration(models.Model):
    user = models.OneToOneField(
        User,
        related_name = '+'
    )
    enabled = models.BooleanField(default = True)

class Decision(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    date = models.DateField()
    suggestion_time_category = models.CharField(
        max_length = 20,
        choices = SuggestionTime.CATEGORIES
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
        if hasattr(settings, 'WALKING_SUGGESTION_SURVEY_DEFAULT_PROBABILITY'):
            return settings.ACTIVITY_SURVEY_DEFAULT_PROBABILITY
        raise ImproperlyConfigured('No default walking suggestion survey decision probability')

class WalkingSuggestionSurveyQuestion(Question):
    pass

class WalkingSuggestionSurvey(Survey):
    
    QUESTION_MODEL = WalkingSuggestionSurveyQuestion
