from datetime import datetime
import random

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from daily_tasks.models import DailyTask

from behavioral_messages.models import MessageTemplate
from days.models import Day
from days.services import DayService
from randomization.models import Decision
from push_messages.models import Message as PushMessage
from surveys.models import Question, Survey, SurveyQuestion, SurveyAnswer, SurveyResponse

User = get_user_model()

class Configuration(models.Model):
    user = models.OneToOneField(User, related_name='morning_message_configuration')
    enabled = models.BooleanField(default=True)

    daily_task = models.OneToOneField(
        DailyTask,
        null=True,
        editable=False,
        related_name='morning_message_configuration',
        on_delete = models.SET_NULL
    )

    def create_daily_task(self):
        if self.daily_task:
            self.destroy_daily_task()
        self.daily_task = DailyTask.create_daily_task(
            user = self.user,
            category = None,
            task = 'morning_messages.tasks.send_morning_message',
            name = 'morning message for %s' % self.user.username,
            arguments = {
                'username': self.user.username
            },
            hour = 6,
            minute = 0
        )
        self.save()

    def destroy_daily_task(self):
        self.daily_task.delete()

    def __str__(self):
        enabled = "disabled"
        if self.enabled:
            enabled = "enabled"
        return "%s (%s)" % (self.user, enabled)

class MorningMessageTemplate(MessageTemplate):
    anchor_message = models.CharField(max_length=255)

class MorningMessageDecision(Decision):

    FRAME_GAIN_ACTIVE = "gain and active"
    FRAME_GAIN_SEDENTARY = "gain and sedentary"
    FRAME_LOSS_ACTIVE = "loss and active"
    FRAME_LOSS_SEDENTARY = "loss and secentary"
    
    FRAMES = [
        FRAME_GAIN_ACTIVE,
        FRAME_GAIN_SEDENTARY,
        FRAME_LOSS_ACTIVE,
        FRAME_LOSS_SEDENTARY
    ]

    FRAME_CHOICES = [(frame, frame) for frame in FRAMES]

    framing = models.CharField(max_length=50, null=True, editable=False, choices=FRAME_CHOICES)

    def get_message_frame(self):
        if self.treated:
            return self.framing
        else:
            return self.set_message_frame()

    def get_random_message_frame(self):
        return random.choice(self.FRAMES + [None, None, None])

    def set_message_frame(self, framing=False):
        if framing is False:
            framing = self.get_random_message_frame()
        self.framing = framing
        self.save()

        self.remove_contexts(['gain', 'loss', 'active', 'sedentary'])
        
        if framing is self.FRAME_GAIN_ACTIVE:
            self.add_context('gain')
            self.add_context('active')
        if framing is self.FRAME_GAIN_SEDENTARY:
            self.add_context('gain')
            self.add_context('sedentary')
        if framing is self.FRAME_LOSS_ACTIVE:
            self.add_context('loss')
            self.add_context('active')
        if framing is self.FRAME_LOSS_SEDENTARY:
            self.add_context('loss')
            self.add_context('sedentary')
        return framing

    def __test_framing(self, frames):
        if self.framing in frames:
            return True
        else:
            return False

    @property
    def is_loss_framed(self):
        return self.__test_framing([self.FRAME_LOSS_ACTIVE, self.FRAME_LOSS_SEDENTARY])
    
    @property
    def is_gain_framed(self):
        return self.__test_framing([self.FRAME_GAIN_ACTIVE, self.FRAME_GAIN_SEDENTARY])

    @property
    def is_sedentary_framed(self):
        return self.__test_framing([self.FRAME_LOSS_SEDENTARY, self.FRAME_GAIN_SEDENTARY])

    @property
    def is_active_framed(self):
        return self.__test_framing([self.FRAME_LOSS_ACTIVE, self.FRAME_GAIN_ACTIVE])

class MorningMessageQuestion(Question):
    pass

class MorningMessageSurvey(Survey):
    QUESTION_MODEL = MorningMessageQuestion
    WORD_OPTIONS = [
        'Energetic',
        'Fatigued',
        'Happy',
        'Sad',
        'Relaxed',
        'Stressed',
        'Tense'
    ]

    selected_word = models.CharField(max_length=50, null=True)
    word_set_string = models.CharField(max_length=225, null=True)

    @property
    def word_set(self):
        return self.get_word_set()

    def get_word_set(self):
        if self.word_set_string:
            words = []
            for word in self.word_set_string.split(','):
                words.append(word.replace(' ', ''))
            if len(words) > 0:
                return words
        return None

    def randomize_word_set(self):
        words = self.WORD_OPTIONS.copy()
        random.shuffle(words)
        self.word_set_string = ','.join(words)

    def get_answers(self):
        answers = super().get_answers()
        answers['selected_word'] = self.selected_word
        return answers

    def get_questions(self):
        questions = super().get_questions()
        questions.append('selected_word')
        return questions

    def get_question_label(self, question_name):
        if question_name == 'selected_word':
            return 'Pick a word'
        else:
            return super().get_question_label(question_name)

    def get_answer_label(self, question_name, answer_value):
        if question_name == 'selected_word':
            return answer_value
        else:
            return super().get_answer_label(question_name, answer_value)

class MorningMessageQuerySet(models.QuerySet):

    NOTIFICATIONS = 'notifications'

    prefetch_methods = {}

    def _clone(self, **kwargs):
        clone = super()._clone(**kwargs)
        clone.prefetch_methods = self.prefetch_methods
        return clone

    def _fetch_all(self):
        super()._fetch_all()
        while self._result_cache and self.prefetch_methods.keys():
            now = datetime.now()
            keys = self.prefetch_methods.keys()
            _key = list(keys).pop()
            method_name = self.prefetch_methods[_key]
            del self.prefetch_methods[_key]
            if hasattr(self, method_name):
                getattr(self, method_name)()
            diff = datetime.now() - now
            print('%s in %d seconds' % (_key, diff.seconds))

    def prefetch_decision(self):
        return self.prefetch_related('message_decision')

    def prefetch_survey(self):
        self.prefetch_methods['survey'] = 'fetch_surveys'
        return self

    def prefetch_message(self):
        self.prefetch_methods['message'] = 'fetch_messages'
        return self

    def prefetch_timezone(self):
        self.prefetch_methods['timezone'] = 'fetch_timezones'
        return self

    def fetch_messages(self):
        morning_message_ids = [_mm.id for _mm in self._result_cache]
        message_by_morning_message_id = {}
        morning_message_id_by_message_id = {}
        message_contexts = MorningMessageContextObject.objects.filter(
            morning_message_id__in = morning_message_ids,
            content_type = ContentType.objects.get_for_model(PushMessage)
        ).all()
        for _message_context in message_contexts:
            message_id = _message_context.object_id
            morning_message_id = _message_context.morning_message_id
            morning_message_id_by_message_id[message_id] = morning_message_id
        messages = PushMessage.objects.filter(
            id__in = morning_message_id_by_message_id.keys()
        ).all()
        for _message in messages:
            morning_message_id = morning_message_id_by_message_id[_message.id]
            message_by_morning_message_id[morning_message_id] = _message

        for _morning_message in self._result_cache:
            if _morning_message.id in message_by_morning_message_id:
                message = message_by_morning_message_id[_morning_message.id]
                _morning_message._message = message

    def fetch_surveys(self):
        survey_by_id = {}
        surveys = MorningMessageSurvey.objects.filter(
            uuid__in = [_mm.survey_id for _mm in self._result_cache]
        ).all()
        for survey in surveys:
            survey_by_id[survey.id] = survey
        questions = SurveyQuestion.objects.filter(
            survey_id__in = survey_by_id.keys()
        ).all()
        for _question in questions:
            survey = survey_by_id[_question.survey_id]
            if not hasattr(survey, '_questions'):
                setattr(survey,'_questions', [])
            survey._questions.append(_question)
        responses = SurveyResponse.objects.filter(
            survey_id__in = survey_by_id.keys()
        ) \
        .exclude(answer = None) \
        .prefetch_related('answer') \
        .all()
        for _response in responses:
            survey = survey_by_id[_response.survey_id]
            if not hasattr(survey, '_answers'):
                setattr(survey,'_answers', {})
            survey._answers[_response.question_id] = _response.answer
        
        for _morning_message in self._result_cache:
            if _morning_message.survey_id in survey_by_id:
                _morning_message.survey = survey_by_id[_morning_message.survey_id]
            else:
                _morning_message.survey = None

    def fetch_timezones(self):
        timezones_by_user_id_then_date = {}
        for _morning_message in self._result_cache:
            if _morning_message.user_id not in timezones_by_user_id_then_date:
                timezones_by_user_id_then_date[_morning_message.user_id] = {}
            timezones_by_user_id_then_date[_morning_message.user_id][_morning_message.date] = None
        filters = []
        for user_id, date_dict in timezones_by_user_id_then_date.items():
            dates = sorted(list(date_dict.keys()))
            filters.append(models.Q(
                user_id = user_id,
                date__gte = dates[0],
                date__lte = dates[len(dates)-1]
            ))
        days_query = None
        for _filter in filters:
            if not days_query:
                days_query = Day.objects.filter(_filter)
            else:
                days_query = days_query.filter(_filter)
        for _day in days_query.all():
            if _day.user_id not in timezones_by_user_id_then_date:
                timezones_by_user_id_then_date[_day.user_id] = {}
            timezones_by_user_id_then_date[_day.user_id][_day.date] = _day.get_timezone()
        for morning_message in self._result_cache:
            _user_id = morning_message.user_id
            _date = morning_message.date
            if _user_id in timezones_by_user_id_then_date:
                if _date in timezones_by_user_id_then_date[_user_id]:
                    morning_message._timezone = timezones_by_user_id_then_date[_user_id][_date]

class MorningMessage(models.Model):

    objects = MorningMessageQuerySet.as_manager()

    user = models.ForeignKey(User)
    date = models.DateField()
    randomized = models.BooleanField(default=True)

    survey = models.ForeignKey(MorningMessageSurvey, null=True, editable=False)

    message_decision = models.ForeignKey(MorningMessageDecision, null=True, editable=False)

    notification = models.CharField(max_length=255, null=True, editable=False)
    text = models.CharField(max_length=255, null=True, editable=False)
    anchor = models.CharField(max_length=255, null=True, editable=False)

    class ContextDoesNotExist(RuntimeError):
        pass

    @property
    def message(self):
        if hasattr(self, '_message'):
            return self._message
        else:
            self._message = self.get_notification()
            return self._message

    @property
    def is_gain_framed(self):
        return self.message_decision.is_gain_framed

    @property
    def is_loss_framed(self):
        return self.message_decision.is_loss_framed

    @property
    def is_sedentary_framed(self):
        return self.message_decision.is_sedentary_framed

    @property
    def is_active_framed(self):
        return self.message_decision.is_active_framed

    def get_notification(self):
        context = MorningMessageContextObject.objects.filter(
            morning_message = self,
            content_type = ContentType.objects.get_for_model(PushMessage)
        ).first()
        if context:
            return context.content_object
        return None

    def __get_context(self, obj):
        try:
            context = MorningMessageContextObject.objects.get(
                morning_message = self,
                content_type = ContentType.objects.get_for_model(obj),
                object_id = obj.id
            )
            return context
        except MorningMessageContextObject.DoesNotExist:
            raise MorningMessage.ContextDoesNotExist('Not found')

    def add_context(self, obj):
        try:
            context = self.__get_context(obj)
            return context
        except MorningMessage.ContextDoesNotExist:
            return MorningMessageContextObject.objects.create(
                morning_message = self,
                content_object = obj
            )

    def get_context(self, obj):
        context = self.__get_context(obj)
        return context.content_object

    def get_timezone(self):
        service = DayService(user=self.user)
        return service.get_timezone_at(self.date)

    @property
    def timezone(self):
        if not hasattr(self, '_timezone'):
            self._timezone = self.get_timezone()            
        return self._timezone

    def remove_context(self, obj):
        try:
            context = self.__get_context(obj)
            context.delete()
        except MorningMessage.ContextDoesNotExist:
            pass
        return True

    def __str__(self):
        return "%s: %s" % (self.user, self.date.strftime("%Y-%m-%d"))

class MorningMessageContextObject(models.Model):
    morning_message = models.ForeignKey(MorningMessage, related_name="context")

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
