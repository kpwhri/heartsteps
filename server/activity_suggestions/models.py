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

class SuggestionTime(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    type = models.CharField(max_length=20, choices=TIME_CATEGORIES)
    
    hour = models.PositiveSmallIntegerField()
    minute = models.PositiveSmallIntegerField()
    timezone = models.CharField(max_length=50, default="America/Los_Angeles")

    user = models.ForeignKey(User)

    scheduled_task = models.OneToOneField(PeriodicTask)

    def make_scheduled_task(self):
        if hasattr(self, 'scheduled_task'):
            return False
        
        utc_time = self.time_as_utc()

        schedule = CrontabSchedule.objects.create(
            minute = utc_time.minute,
            hour = utc_time.hour,
        )
        self.scheduled_task = PeriodicTask.objects.create(
            crontab = schedule,
            name = 'Activity suggestion %s for %s' % (self.type, self.user),
            task = 'activity_suggestions.tasks.start_decision',
            kwargs = json.dumps({
                'username': self.user.username,
                'time_category': self.type
            })
        )
        return True

    def time_as_utc(self):
        now = datetime.now()
        dt = datetime(now.year, now.month, now.day, self.hour, self.minute)

        #Add timezone and convert
        tz = pytz.timezone(self.timezone)
        return tz.normalize(tz.localize(dt)).astimezone(pytz.utc)


    def __str__(self):
        return "%s:%s (%s) - %s" % (self.hour, self.minute, self.type, self.user)

@receiver(pre_save, sender=SuggestionTime)
def pre_save_suggested_time(sender, instance, *args, **kwargs):
    instance.make_scheduled_task()

@receiver(post_delete, sender=SuggestionTime)
def pre_delete_suggested_time(sender, instance, *args, **kwargs):
    if hasattr(instance, 'scheduled_task'):
        instance.scheduled_task.crontab.delete()
        instance.scheduled_task.delete()

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