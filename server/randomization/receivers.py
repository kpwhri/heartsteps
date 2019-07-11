from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import Decision

@receiver(pre_save)
def update_avaiable(sender, instance, *args, **kwargs):
    if isinstance(instance, Decision):
        instance.availability = instance.is_available()
