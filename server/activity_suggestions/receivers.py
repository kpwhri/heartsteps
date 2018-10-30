from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from locations.services import LocationService
from locations.signals import timezone_updated

from .models import Configuration, DailyTask

@receiver(post_save, sender=Configuration)
def post_save_configuration(sender, instance, *args, **kwargs):
    instance.update_daily_tasks()

@receiver(post_delete, sender=DailyTask)
def pre_delete_suggested_time(sender, instance, *args, **kwargs):
    instance.delete_task()

@receiver(timezone_updated, sender=User)
def timezone_updated_receiver(sender, username, *args, **kwargs):
    configuration = Configuration.objects.get(user__username=username)
    configuration.update_daily_tasks()