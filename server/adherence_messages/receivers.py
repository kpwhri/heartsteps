from datetime import date

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from participants.signals import initialize_participant

from .models import Configuration
from .models import AdherenceDay
from .models import DailyAdherenceMetric
from .models import User

@receiver(initialize_participant, sender=User)
def enable_configuration(sender, user, *args, **kwargs):
    Configuration.objects.update_or_create(
        user = user,
        defaults = {
            'enabled': True
        }
    )

@receiver(pre_save, sender=Configuration)
def pre_save(sender, instance, *args, **kwargs):
    if instance.hour is None or instance.minute is None:
        instance.set_default_time()
    instance.update_daily_task()
    instance.set_initialized_date()
