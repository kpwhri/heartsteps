from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from days.signals import timezone_updated

from .models import DailyTask

@receiver(timezone_updated, sender=User)
def timezone_updated_receiver(sender, username, **kwargs):
    for daily_task in DailyTask.objects.filter(user__username=username).all():
        daily_task.update_timezone()

@receiver(post_delete, sender=DailyTask)
def pre_delete_suggested_time(sender, instance, *args, **kwargs):
    instance.delete_task()
