from django.db import models
from django.contrib.auth import get_user_model

from days.services import DayService
from daily_tasks.models import DailyTask
from sms_messages.models import Message
from sms_messages.services import SMSService

User = get_user_model()

CLOSEOUT_MESSAGE = 'You have completed your time in the HeartSteps study – thank you! Please text back with "Yes" if you would like to continue using the HeartSteps app. If we don\'t hear from you within a week, we will disable your HeartSteps account and stop collecting your data. (Your Fitbit and Fitbit app will still work, however). Thanks again and please call 866-648-1775 with questions.'

class Configuration(models.Model):

    class MessageAlreadySent(RuntimeError):
        pass

    class ConfigurationDisabled(RuntimeError):
        pass

    class BeforeCloseoutDate(RuntimeError):
        pass

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = '+'
    )
    closeout_date = models.DateField()
    message = models.ForeignKey(
        Message,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    daily_task = models.ForeignKey(
        DailyTask,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    @property
    def enabled(self):
        if self.daily_task_id:
            return self.daily_task.enabled
        else:
            return False

    def enable(self):
        if self.message_id:
            raise Configuration.MessageAlreadySent('Will not activate as message already sent')
        if not self.daily_task_id:
            task = DailyTask.objects.create(
                user = self.user
            )
            task.create_task(
                task = 'closeout_messages.tasks.send_closeout_message',
                name = '%s send closeout message' % (self.user.username),
                arguments = {
                    'username': self.user.username
                }
            )
            self.daily_task = task
            self.save()
        self.daily_task.set_time(
            hour = 19,
            minute = 0
        )
        self.daily_task.enable()

    def disable(self):
        if self.daily_task_id:
            self.daily_task.disable()

    def send_message(self):
        if not self.enabled:
            raise Configuration.ConfigurationDisabled('Configuration disable, will not send message')
        if self.message:
            raise Configuration.MessageAlreadySent('Will not send message twice')
        day_service = DayService(user = self.user)
        current_date = day_service.get_current_date()
        if current_date < self.closeout_date:
            raise Configuration.BeforeCloseoutDate('Will not send before closeout date')
        sms_service = SMSService(user = self.user)
        self.message = sms_service.send(CLOSEOUT_MESSAGE)
        self.save()
        self.disable()


    def __str__(self):
        return "{date} ({user_id})".format(
            user_id = self.user_id,
            date = self.closeout_date
        )
