from django.db import models
from django.contrib.auth import get_user_model

from daily_tasks.models import DailyTask

from behavioral_messages.models import MessageTemplate, ContextTag
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
    pass
