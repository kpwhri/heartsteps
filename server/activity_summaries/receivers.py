from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save

from fitbit_api.services import FitbitService

from .models import ActivityLog, Day, FitbitDay

@receiver(post_save, sender=ActivityLog)
def activity_log_updates_day(sender, instance, *args, **kwargs):
    activity_log = instance
    try:
        day = Day.objects.get(
            user = activity_log.user,
            date__year = activity_log.start.year,
            date__month = activity_log.start.month,
            date__day = activity_log.start.day
        )
    except Day.DoesNotExist:
        day = Day.objects.create(
            user = activity_log.user,
            date = date(activity_log.start.year, activity_log.start.month, activity_log.start.day)
        )
    day.update_from_activities()

@receiver(post_save, sender=FitbitDay)
def fitbit_day_updates_day(sender, instance, *args, **kwargs):
    fitbit_day = instance
    fitbit_service = FitbitService(account=instance.account)
    for user in fitbit_service.get_users():
        try:
            day = Day.objects.get(
                user = user,
                date__year = fitbit_day.date.year,
                date__month = fitbit_day.date.month,
                date__day = fitbit_day.date.day
            )
        except Day.DoesNotExist:
            day = Day.objects.create(
                user = user,
                date = fitbit_day.date
            )
        day.update_from_fitbit()
