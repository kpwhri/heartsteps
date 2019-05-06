import random

from django.db import models
from django.contrib.auth import get_user_model

from daily_tasks.models import DailyTask

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision
from surveys.models import Question, Survey

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

class MorningMessageQuestion(Question):
    pass

class MorningMessageSurvey(Survey):
    QUESTION_MODEL = MorningMessageQuestion
    WORD_PAIR_SETS = [
        [
            ('Alert', 'Fatigued'),
            ('Excited', 'Bored'),
            ('Elated', 'Depressed'),
            ('Happy', 'Sad')
        ],
        [
            ('Tense', 'Calm'),
            ('Nervous', 'Relaxed'),
            ('Stressed', 'Serene'),
            ('Upset', 'Contented')
        ]
    ]

    word_set_string = models.CharField(max_length=225, null=True)
    selected_word = models.CharField(max_length=50, null=True)

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
        words = []
        for word_set in self.WORD_PAIR_SETS:
            pair = random.choice(word_set)
            words.append(pair[0])
            words.append(pair[1])
        random.shuffle(words)
        self.word_set_string = ','.join(words)

class MorningMessage(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    randomized = models.BooleanField(default=True)

    survey = models.ForeignKey(MorningMessageSurvey, null=True, editable=False)

    message_decision = models.ForeignKey(MorningMessageDecision, null=True, editable=False)

    notification = models.CharField(max_length=255, null=True, editable=False)
    text = models.CharField(max_length=255, null=True, editable=False)
    anchor = models.CharField(max_length=255, null=True, editable=False)

    def __str__(self):
        return "%s: %s" % (self.user, self.date.strftime("%Y-%m-%d"))
