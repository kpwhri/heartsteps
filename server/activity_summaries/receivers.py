from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from days.services import DayService
from fitbit_api.services import FitbitService
from fitbit_activities.models import FitbitDay

from .models import ActivityLog, Day

def list_and_create_day(user, date):
    day_query = Day.objects.filter(
        user = user,
        date = date
    )
    if day_query.count():
        return list(day_query.all())
    else:
        day = Day.objects.create(
            user = user,
            date = date
        )
        return [day]

def activity_log_updates_day(sender, instance, *args, **kwargs):
    activity_log = instance
    
    day_service = DayService(user = activity_log.user)
    local_timezone = day_service.get_timezone_at(activity_log.start)
    local_time = activity_log.start.astimezone(local_timezone)
    local_date = date(
        local_time.year,
        local_time.month,
        local_time.day
    )

    for day in list_and_create_day(activity_log.user, local_date):
        day.update_from_activities()

post_save.connect(activity_log_updates_day, sender=ActivityLog)
post_delete.connect(activity_log_updates_day, sender=ActivityLog)


@receiver(post_save, sender=FitbitDay)
def fitbit_day_updates_day(sender, instance, *args, **kwargs):
    fitbit_day = instance
    fitbit_service = FitbitService(account=instance.account)
    for user in fitbit_service.get_users():
        for day in list_and_create_day(user, fitbit_day.date):
            day.update_from_fitbit()
