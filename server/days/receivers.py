from django.dispatch import receiver
from django.db.models.signals import post_save

from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService

from .models import Day

@receiver(post_save, sender=FitbitDay)
def update_timezone_from_fitbit(sender, instance, *args, **kwargs):
    service = FitbitService(account=instance.account)
    for user in service.get_users():
        Day.objects.update_or_create(
            user = user,
            date = instance.date,
            defaults = {
                "timezone": instance._timezone
            }
        )