from django.db import models

import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from daily_tasks.models import DailyTask
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

    @property
    def daily_tasks(self):
        if not hasattr(self,'_daily_tasks'):
            self._daily_tasks = self.get_daily_tasks()
        return self._daily_tasks

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

    def get_daily_tasks(self):
        daily_tasks = DailyTask.objects.filter(
            user=self.user,
            category__contains='wss-'
        ).all()
        return list(daily_tasks)

    def update_survey_times(self):
        suggestion_times = SuggestionTime.objects.filter(user=self.user).all()
        daily_tasks = self.get_daily_tasks()
        for suggestion_time in suggestion_times:
            suggestion_time_category = 'wss-' + suggestion_time.category
            daily_task_categories = [daily_task.category for daily_task in daily_tasks]
            try:
                index = daily_task_categories.index(suggestion_time_category)
                daily_task = daily_tasks.pop(index)
                daily_task.update_task(
                    task = 'walking_suggestion_surveys.tasks.randomize_walking_suggestion_survey',
                    name = 'randomize-walking-suggestion-survey-{category}-{username}'.format(
                        category = suggestion_time.category,
                        username = self.user.username
                    ),
                    arguments = {
                        'username': self.user.username
                    } 
                )
                daily_task.set_time(
                    hour = suggestion_time.hour,
                    minute = suggestion_time.minute
                )
            except ValueError:
                DailyTask.create_daily_task(
                    user = self.user,
                    category = suggestion_time_category,
                    task = 'walking_suggestion_surveys.tasks.randomize_walking_suggestion_survey',
                    name = 'randomize-walking-suggestion-survey-{category}-{username}'.format(
                        category = suggestion_time.category,
                        username = self.user.username
                    ),
                    arguments = {
                        'username': self.user.username
                    },
                    hour = suggestion_time.hour,
                    minute = suggestion_time.minute
                )
        for daily_task in daily_tasks:
            daily_task.delete()
        


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
        if treatment_probability is None:
            if self.treatment_probability is not None:
                treatment_probability = self.treatment_probability
            else:
                treatment_probability = self.get_default_probability()
        if random.random() < treatment_probability:
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
