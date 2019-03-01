from datetime import date

from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import pre_save, post_save

from weekly_reflection.models import ReflectionTime

from weeks.services import WeekService

@receiver(pre_save, sender=ReflectionTime)
def pre_save_update_daily_task(sender, instance, *args, **kwargs):
    if not instance.daily_task:
        instance.create_daily_task()
    else:
        instance.update_daily_task()
    if instance.active:
        instance.daily_task.enable()
    else:
        instance.daily_task.disable()
