from django.db import models

import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from push_messages.services import PushMessageService

from surveys.models import Question
from surveys.models import Survey
from surveys.serializers import SurveySerializer
from walking_suggestion_times.models import SuggestionTime

User = get_user_model()

class Configuration(models.Model):
    user = models.OneToOneField(
        User,
        related_name = '+'
    )
    enabled = models.BooleanField(default = True)
    treatment_probability = models.FloatField(null=True)

    def randomize_survey(self):
        decision = Decision.objects.create(
            user = self.user
        )
        if decision.treated:
            return self.create_survey()
        else:
            return None
    
    def create_survey(self):
        survey = WalkingSuggestionSurvey.objects.create(
            user = self.user
        )
        survey.reset_questions()
        return survey


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

    class NotificationSendError(RuntimeError):
        pass

    def send_notification(self):
        serialized_survey = SurveySerializer(self)
        try:
            service = PushMessageService(user = self.user)
            message = service.send_notification(
                body = 'Can you answer a couple of questions?',
                title = 'Walking Suggestion Survey',
                collapse_subject = 'walking_suggestion_survey',
                data = {
                    'survey':serialized_survey.data
                }
            )
            return message
        except (PushMessageService.MessageSendError, PushMessageService.DeviceMissingError) as e:
            raise WalkingSuggestionSurvey.NotificationSendError('Unable to send notification')  
