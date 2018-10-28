import uuid, json, pytz
from datetime import datetime

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver

from django.contrib.auth.models import User

from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule

from randomization.models import Decision, ContextTag

class SuggestionTime(models.Model):

    MORNING = 'morning'
    LUNCH = 'lunch'
    MIDAFTERNOON = 'midafternoon'
    EVENING = 'evening'
    POSTDINNER = 'postdinner'

    TIMES = [MORNING, LUNCH, MIDAFTERNOON, EVENING, POSTDINNER]

    CATEGORIES = [
        (MORNING, 'Morning'),
        (LUNCH, 'Lunch'),
        (MIDAFTERNOON, 'Afternoon'),
        (EVENING, 'Evening'),
        (POSTDINNER, 'Post dinner')
    ]

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)

    user = models.ForeignKey(User)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    hour = models.PositiveSmallIntegerField()
    minute = models.PositiveSmallIntegerField()

    def __str__(self):
        return "%s:%s (%s) - %s" % (self.hour, self.minute, self.type, self.configuration.user)         

class Configuration(models.Model):

    NIGHTLY_TASK_CATEGORY = 'nightly update'

    user = models.ForeignKey(User)
    enabled = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default="America/Los_Angeles")

    def update_daily_tasks(self):
        for suggestion_time in SuggestionTime.objects.filter(user=self.user).all():
            self.update_suggestion_time_task(suggestion_time)
        try:
            daily_task = DailyTask.objects.get(
                configuration = self,
                category = self.NIGHTLY_TASK_CATEGORY
            )
        except DailyTask.DoesNotExist:
            daily_task = self.create_nightly_task()
        daily_task.set_time(1, 30, self.timezone)

    def update_suggestion_time_task(self, suggestion_time):
        daily_task, created = DailyTask.objects.get_or_create(
            configuration = self,
            category = suggestion_time.category
        )
        if created:
            daily_task.create_task(
                task = 'activity_suggestions.tasks.start_decision',
                name = 'Activity suggestion %s for %s' % (suggestion_time.category, self.user),
                arguments = {
                    'username': self.user.username,
                    'category': suggestion_time.category
                }
            )
        daily_task.set_time(
            hour = suggestion_time.hour,
            minute = suggestion_time.minute,
            timezone = self.timezone
        )

    def create_nightly_task(self):
        daily_task = DailyTask.objects.create(
            configuration = self,
            category = self.NIGHTLY_TASK_CATEGORY
        )
        daily_task.create_task(
            task = 'activity_suggestions.tasks.update_activity_suggestion_service',
            name = 'Activity suggestion nightly update for %s' % self.user,
            arguments = {
                'username': self.user.username
            }
        )
        return daily_task

    def __str__(self):
        if self.enabled:
            return "%s Enabled" % self.user
        else:
            return "%s Disabled" % self.user

@receiver(post_save, sender=Configuration)
def post_save_configuration(sender, instance, *args, **kwargs):
    instance.update_daily_tasks()

class DailyTask(models.Model):
    configuration = models.ForeignKey(Configuration)
    category = models.CharField(max_length=20)
    task = models.ForeignKey(PeriodicTask, null=True)

    def create_task(self, task, name, arguments):
        self.task = PeriodicTask.objects.create(
            crontab = CrontabSchedule.objects.create(),
            name = name,
            task = task,
            kwargs = json.dumps(arguments)
        )
        self.save()

    def set_time(self, hour, minute, timezone):
        time = datetime.now(pytz.timezone(timezone)).replace(
            hour = hour,
            minute = minute
        )
        utc_time = time.astimezone(pytz.utc)
        self.task.crontab.hour = utc_time.hour
        self.task.crontab.minute = utc_time.minute
        self.task.crontab.save()
        PeriodicTasks.changed(self.task)

    def delete_task():
        self.task.crontab.delete()
        self.task.delete()

@receiver(post_delete, sender=DailyTask)
def pre_delete_suggested_time(sender, instance, *args, **kwargs):
    instance.delete_task()

class ActivitySuggestionDecisionManager(models.Manager):

    def get_queryset(self):
        return Decision.objects.filter(tags__tag="activity suggestion")

class ActivitySuggestionDecision(Decision):
    objects = ActivitySuggestionDecisionManager()

    class Meta:
        proxy = True

class ServiceRequest(models.Model):
    user = models.ForeignKey(User)
    url = models.CharField(max_length=150)

    request_data = models.TextField()
    request_time = models.DateTimeField()

    response_code = models.IntegerField()
    response_data = models.TextField()
    response_time = models.DateTimeField()

    def __str__(self):
        return "%s (%d) %s" % (self.user, self.response_code, self.url)