from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from morning_messages.models import Configuration

@receiver(pre_save, sender=Configuration)
def manage_daily_task(sender, instance, **kwargs):
    if not instance.daily_task:
        instance.create_daily_task()
    if instance.enabled:
        instance.daily_task.enable()
    if not instance.enabled:
        instance.daily_task.disable()

@receiver(pre_delete, sender=Configuration)
def delete_daily_task(sender, instance, **kwargs):
    if instance.daily_task:
        instance.destroy_daily_task()
