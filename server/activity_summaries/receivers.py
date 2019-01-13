from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from locations.services import LocationService
from fitbit_api.services import FitbitService
from fitbit_api.models import FitbitDay

from .models import ActivityLog, Day

def activity_log_updates_day(sender, instance, *args, **kwargs):
    activity_log = instance
    
    location_service = LocationService(user = activity_log.user)
    local_timezone = location_service.get_timezone_on(activity_log.start)
    local_time = activity_log.start.astimezone(local_timezone)

    try:
        day = Day.objects.get(
            user = activity_log.user,
            date__year = local_time.year,
            date__month = local_time.month,
            date__day = local_time.day
        )
    except Day.DoesNotExist:
        day = Day.objects.create(
            user = activity_log.user,
            date = date(local_time.year, local_time.month, local_time.day)
        )
    day.update_from_activities()

post_save.connect(activity_log_updates_day, sender=ActivityLog)
post_delete.connect(activity_log_updates_day, sender=ActivityLog)


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
