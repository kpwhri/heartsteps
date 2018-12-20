import random

from django.db import models
from django.contrib.auth import get_user_model

from daily_tasks.models import DailyTask

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision

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
        if self.a_it:
            return self.framing
        framing = random.choice(self.FRAMES + [None, None, None])
        self.framing = framing
        self.a_it = True
        self.save()

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
