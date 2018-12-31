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

@receiver(post_save, sender=ReflectionTime)
def post_save_update_weekend(sender, instance, *args, **kwargs):
    service = WeekService(user = instance.user)
    next_run = instance.get_next_time()
    end_of_week = date(next_run.year, next_run.month, next_run.day)
    try:
        week = service.get_week_for_date(timezone.now())
        week.end_date = end_of_week
        week.save()
    except WeekService.WeekDoesNotExist:
        week = service.create_week(
            end_date = end_of_week
        )
