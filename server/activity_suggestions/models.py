import uuid, json, pytz
from datetime import datetime

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete, post_delete, pre_save
from django.dispatch import receiver

from django.contrib.auth.models import User

from django_celery_beat.models import PeriodicTask, CrontabSchedule

from randomization.models import Decision, ContextTag

MORNING = 'morning'
LUNCH = 'lunch'
MIDAFTERNOON = 'midafternoon'
EVENING = 'evening'
POSTDINNER = 'postdinner'

TIMES = [MORNING, LUNCH, MIDAFTERNOON, EVENING, POSTDINNER]

TIME_CATEGORIES = [
    (MORNING, 'Morning'),
    (LUNCH, 'Lunch'),
    (MIDAFTERNOON, 'Afternoon'),
    (EVENING, 'Evening'),
    (POSTDINNER, 'Post dinner')
]

class SuggestionTimeConfiguration(models.Model):
    user = models.ForeignKey(User)
    enabled = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default="America/Los_Angeles")

    def __str__(self):
        if self.enabled:
            return "%s Enabled" % self.user
        else:
            return "%s Disabled" % self.user

class SuggestionTime(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)

    configuration = models.ForeignKey(SuggestionTimeConfiguration, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TIME_CATEGORIES)
    
    hour = models.PositiveSmallIntegerField()
    minute = models.PositiveSmallIntegerField()

    scheduled_task = models.OneToOneField(PeriodicTask)

    def create_task(self):        
        utc_time = self.time_as_utc()

        schedule = CrontabSchedule.objects.create(
            minute = utc_time.minute,
            hour = utc_time.hour,
        )
        scheduled_task = PeriodicTask(
            crontab = schedule,
            name = 'Activity suggestion %s for %s' % (self.type, self.configuration.user),
            task = 'activity_suggestions.tasks.start_decision',
            kwargs = json.dumps({
                'username': self.configuration.user.username,
                'time_category': self.type
            }),
            enabled = False
        )
        if self.configuration.enabled:
            scheduled_task.enabled = True
        scheduled_task.save()
        self.scheduled_task = scheduled_task
    
    def delete_task(self):
        self.scheduled_task.crontab.delete()
        self.scheduled_task.delete()

    def time_as_utc(self):
        now = datetime.now()
        dt = datetime(now.year, now.month, now.day, self.hour, self.minute)

        #Add timezone and convert
        timezone = self.configuration.timezone
        tz = pytz.timezone(timezone)
        return tz.normalize(tz.localize(dt)).astimezone(pytz.utc)


    def __str__(self):
        return "%s:%s (%s) - %s" % (self.hour, self.minute, self.type, self.configuration.user)

@receiver(pre_save, sender=SuggestionTime)
def pre_save_suggested_time(sender, instance, *args, **kwargs):
    if hasattr(instance, 'scheduled_task'):
        instance.update_task()
    else:
        instance.create_task()

@receiver(post_delete, sender=SuggestionTime)
def pre_delete_suggested_time(sender, instance, *args, **kwargs):
    instance.delete_task()
        

class ActivitySuggestionDecisionManager(models.Manager):

    def get_queryset(self):
        return Decision.objects.filter(tags__tag="activity suggestion")

class ActivitySuggestionDecision(Decision):
    objects = ActivitySuggestionDecisionManager()

    class Meta:
        proxy = True

class ActivitySuggestionServiceRequest(models.Model):
    user = models.ForeignKey(User)
    url = models.CharField(max_length=150)

    request_data = models.TextField()
    request_time = models.DateTimeField()

    response_code = models.IntegerField()
    response_data = models.TextField()
    response_time = models.DateTimeField()

    def __str__(self):
        return "%s (%d) %s" % (self.user, self.response_code, self.url)