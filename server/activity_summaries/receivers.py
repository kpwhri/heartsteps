from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from days.services import DayService
from fitbit_api.services import FitbitService
from fitbit_activities.models import FitbitDay

from .models import ActivityLog, Day

def activity_log_updates_day(sender, instance, *args, **kwargs):
    activity_log = instance
    
    day_service = DayService(user = activity_log.user)
    local_timezone = day_service.get_timezone_at(activity_log.start)
    local_time = activity_log.start.astimezone(local_timezone)

    day, _ = Day.objects.get_or_create(
        user = activity_log.user,
        date = date(
            local_time.year,
            local_time.month,
            local_time.day
        )
    )
    day.update_from_activities()

post_save.connect(activity_log_updates_day, sender=ActivityLog)
post_delete.connect(activity_log_updates_day, sender=ActivityLog)


@receiver(post_save, sender=FitbitDay)
def fitbit_day_updates_day(sender, instance, *args, **kwargs):
    fitbit_day = instance
    fitbit_service = FitbitService(account=instance.account)
    for user in fitbit_service.get_users():
        day, _ = Day.objects.get_or_create(
            user = user,
            date = fitbit_day.date
        )
        day.update_from_fitbit()
