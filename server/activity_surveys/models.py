from django.db import models
from django.contrib.auth import get_user_model

from surveys.models import Question
from surveys.models import Survey

User = get_user_model()

class Configuration(models.Model):
    user = models.OneToOneField(
        User,
        related_name = '+'
    )
    enabled = models.BooleanField(default = True)

class ActivitySurvey(Survey):
    pass
