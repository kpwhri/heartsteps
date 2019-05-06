from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import ActivityPlan

@receiver(pre_save, sender=ActivityPlan)
def pre_save_activity_plan(sender, instance, *args, **kwargs):
    start_time = instance.impute_start_datetime()
    instance.start = start_time
