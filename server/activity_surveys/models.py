from django.db import models
from django.contrib.auth import get_user_model

from fitbit_activities.models import FitbitActivity
from surveys.models import Question
from surveys.models import Survey

User = get_user_model()

class Configuration(models.Model):
    user = models.OneToOneField(
        User,
        related_name = '+'
    )
    enabled = models.BooleanField(default = True)

class ActivitySurveyQuestion(Question):
    pass

class ActivitySurvey(Survey):
    
    QUESTION_MODEL = ActivitySurveyQuestion

    fitbit_activity = models.ForeignKey(
        FitbitActivity,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

