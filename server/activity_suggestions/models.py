import uuid
from django.db import models
from django.db.models.signals import pre_delete, post_delete, pre_save
from django.dispatch import receiver

from django.contrib.auth.models import User

from django_celery_beat.models import PeriodicTask, CrontabSchedule

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

    user = models.ForeignKey(User)

    scheduled_task = models.OneToOneField(PeriodicTask)

    def make_scheduled_task(self):
        if self.scheduled_task:
            return False
        schedule = CrontabSchedule.objects.create(
            minute = self.minute,
            hour = self.hour
        )
        self.scheduled_task = PeriodicTask.objects.create(
            crontab = schedule,
            name = 'Activity suggestion %s for %s' % (self.type, self.user)
        )
        return True


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