from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService

from .models import Day
from .models import User
from .services import DayService
from .signals import timezone_updated

@receiver(pre_save, sender=Day)
def set_day_start_and_end_times(sender, instance, *args, **kwargs):
    day = instance
    if not day.start:
        day.set_start()
    if not day.end:
        day.set_end()

        

@receiver(post_save, sender=FitbitDay)
def update_timezone_from_fitbit(sender, instance, *args, **kwargs):
    fitbit_service = FitbitService(account=instance.account)
    for user in fitbit_service.get_users():
        query = Day.objects.filter(user=user, date=instance.date)

        if not query.exists():
            Day.objects.create(user=user, date=instance.date, timezone=instance._timezone)
        else:
            query.update(timezone=instance._timezone)

        day_service = DayService(user=user)
        current_date = day_service.get_current_date()
        if current_date == instance.date:
            timezone_updated.send(User, username=user.username)