from datetime import timedelta

from django.db import models
from django.utils import timezone

import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from daily_tasks.models import DailyTask
from days.models import LocalizeTimezoneQuerySet
from days.services import DayService
from push_messages.models import Message
from push_messages.services import PushMessageService
from surveys.models import Question
from surveys.models import Survey
from surveys.models import SurveyQuerySet
from surveys.serializers import SurveySerializer
from walking_suggestion_times.models import SuggestionTime

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
    def daily_tasks(self):
        if not hasattr(self,'_daily_tasks'):
            self._daily_tasks = self.get_daily_tasks()
        return self._daily_tasks
    
    @property
    def last_survey(self):
        if not hasattr(self, '_last_survey'):
            self._last_survey = self.get_last_survey()
        return self._last_survey

    @property
    def last_survey_answered_datetime(self):
        service = DayService(user=self.user)
        if self.last_survey.answered:
            return service.get_datetime_at(self.last_survey.updated)
        return None

    @property
    def last_survey_sent_datetime(self):
        service = DayService(user=self.user)
        if self.last_survey.created:
            return service.get_datetime_at(self.last_survey.created)
        return None

    @property
    def last_answered_survey(self):
        if not hasattr(self, '_last_answered_survey'):
            self._last_answered_survey = self.get_last_answered_survey()
        return self._last_answered_survey

    @property
    def last_answered_survey_datetime(self):
        service = DayService(user=self.user)
        if self.last_answered_survey:
            return service.get_datetime_at(self.last_answered_survey.updated)
        return None

    @property
    def last_decision(self):
        if not hasattr(self, '_last_decision'):
            self._last_decision = self.get_last_decision()
        return self._last_decision

    @property
    def summary_of_last_24_hours(self):
        if not hasattr(self, '_summary_of_last_24_hours'):
            self._summary_of_last_24_hours = self.get_summary_of_last_24_hours()
        return self._summary_of_last_24_hours

    @property
    def summary_of_last_7_days(self):
        if not hasattr(self, '_summary_of_last_7_days'):
            self._summary_of_last_7_days = self.get_summary_of_last_7_days()
        return self._summary_of_last_7_days

    def get_summary_of_last_24_hours(self):
        surveys = WalkingSuggestionSurvey.objects.filter(
            user = self.user,
            created__gte = timezone.now() - timedelta(days=1)
        ).all()

        return Configuration.summarize_walking_suggestion_surveys(surveys)

    def get_summary_of_last_7_days(self):
        surveys = WalkingSuggestionSurvey.objects.filter(
            user = self.user,
            created__gte = timezone.now() - timedelta(days=7)
        ).all()

        return Configuration.summarize_walking_suggestion_surveys(surveys)

    def summarize_walking_suggestion_surveys(surveys):
        return {
            'sent': sum([1 for survey in surveys]),
            'answered': sum([1 for survey in surveys if survey.answered])
        }

    def get_last_decision(self):
        return Decision.objects.filter(
            user = self.user
        ) \
        .last()

    def get_last_survey(self):
        return WalkingSuggestionSurvey.objects.filter(
            user = self.user
        ) \
        .order_by('created') \
        .last()

    def get_last_answered_survey(self):
        return WalkingSuggestionSurvey.objects.filter(
            user = self.user,
            answered = True
        ) \
        .order_by('created') \
        .last()

    def get_current_date(self):
        service = DayService(user=self.user)
        return service.get_current_date()

    def get_current_datetime(self):
        service = DayService(user=self.user)
        return service.get_current_datetime()

    def get_current_suggestion_time_category(self):
        current_datetime = self.get_current_datetime()
        suggestion_time_differences = []
        for suggestion_time in SuggestionTime.objects.filter(user=self.user).all():
            suggestion_time_today = suggestion_time.get_datetime_for_today()
            if suggestion_time_today >= current_datetime:
                difference = suggestion_time_today - current_datetime
            else:
                difference = current_datetime - suggestion_time_today
            suggestion_time_differences.append((difference.seconds, suggestion_time))
        sorted_suggestion_time_differences = sorted(suggestion_time_differences, key=lambda x: x[0])
        if len(sorted_suggestion_time_differences) > 0:
            smallest_difference = sorted_suggestion_time_differences[0][0]
            suggestion_time = sorted_suggestion_time_differences[0][1]
            if smallest_difference <= 60*90:
                return suggestion_time.category
        return None

    def randomize_survey(self):
        suggestion_time_category = self.get_current_suggestion_time_category()
        if suggestion_time_category:
            current_date = self.get_current_date()
            number_of_similar_decisions = Decision.objects.filter(
                date = current_date,
                suggestion_time_category = suggestion_time_category,
                user = self.user
            ).count()
            if number_of_similar_decisions == 0:
                decision = Decision(
                    date = current_date,
                    suggestion_time_category = suggestion_time_category,
                    treatment_probability = self.treatment_probability,
                    user = self.user
                )
                decision.randomize()
                if decision.treated:
                    survey = self.create_survey()
                    decision.survey = survey
                    
                    try:
                        decision.notification = survey.send_notification()
                    except WalkingSuggestionSurvey.NotificationSendError:
                        pass
                decision.save()
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
        
class DecisionQuerySet(LocalizeTimezoneQuerySet):

    _preload_surveys = False
    _surveys_loaded = False
    _localize_datetimes = False
    _localized_datetimes = False

    def _clone(self, **kwargs):
        clone = super()._clone(**kwargs)
        clone._preload_surveys = self._preload_surveys
        clone._surveys_loaded = self._surveys_loaded
        clone._localize_datetimes = self._localize_datetimes
        clone._localized_datetimes = self._localized_datetimes
        return clone

    def _fetch_all(self):
        super()._fetch_all()
        if self._result_cache and self._preload_surveys and not self._surveys_loaded:
            self._load_surveys()
            self._surveys_loaded = True

        if self._result_cache and self._localize_datetimes and not self._localized_datetimes:
            self._load_timezones()
            self._localized_datetimes = True

    def preload_surveys(self):
        self._preload_surveys = True
        return self

    def _load_surveys(self):
        survey_ids = [decision.survey_id for decision in self._result_cache if decision.survey_id]
        surveys = WalkingSuggestionSurvey.objects.filter(uuid__in=survey_ids) \
        .preload_answers() \
        .all()
        survey_by_id = {}
        for survey in surveys:
            survey_by_id[str(survey.uuid)] = survey
        for decision in self._result_cache:
            if decision.survey_id and decision.survey_id in survey_by_id:
                decision.survey = survey_by_id[str(decision.survey_id)]

    def localize_timezone(self):
        self._localize_datetimes = True
        return self

    def _load_timezones(self):
        user_ids = []
        start = None
        end = None
        for decision in self._result_cache:
            if decision.user_id not in user_ids:
                user_ids.append(decision.user_id)
            if not start or decision.created < start:
                start = decision.created
            if not end or decision.created > end:
                end = decision.created
        timezone_dict = self.cache_timezones(user_ids, start, end)
        for decision in self._result_cache:
            decision.created = self.set_timezone(timezone_dict, decision.user_id, decision.created)
            if decision.notification:
                message_receipts = decision.notification.get_message_receipts()
                for key, value in message_receipts.items():
                    message_receipts[key] = self.set_timezone(timezone_dict, decision.user_id, value)
                decision.notification.set_message_receipts(message_receipts)

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

    survey = models.ForeignKey(
        'WalkingSuggestionSurvey',
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
    notification = models.ForeignKey(
        Message,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = DecisionQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.treated is None:
            self.randomize()
        super().save(*args, **kwargs)
        
    @property
    def randomized_at(self):
        return self.created

    def randomize(self):
        if self.treatment_probability is None:
            self.treatment_probability = self.get_default_probability()
        if random.random() < self.treatment_probability:
            self.treated = True
        else:
            self.treated = False
        
    def get_default_probability(self):
        try:
            configuration = Configuration.objects.get(user=self.user)
            if configuration.treatment_probability is not None:
                return configuration.treatment_probability
        except Configuration.DoesNotExist:
            pass
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
                },
                send_message_id_only = True
            )
            return message
        except (PushMessageService.MessageSendError, PushMessageService.DeviceMissingError) as e:
            raise WalkingSuggestionSurvey.NotificationSendError('Unable to send notification')  
