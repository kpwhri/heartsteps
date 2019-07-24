from datetime import date
from datetime import timedelta

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.template.loader import render_to_string
from django.utils import timezone

from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccountUser
from page_views.models import PageView
from participants.models import Participant
from participants.signals import initialize_participant

from .models import AdherenceMetric
from .models import Configuration
from .models import User
from .tasks import initialize_adherence

@receiver(initialize_participant, sender=Participant)
def enable_configuration(sender, participant, *args, **kwargs):
    Configuration.objects.update_or_create(
        user = participant.user,
        defaults = {
            'enabled': True
        }
    )

@receiver(pre_save, sender=Configuration)
def pre_save(sender, instance, *args, **kwargs):
    if instance.hour is None or instance.minute is None:
        instance.set_default_time()
    instance.update_daily_task()

@receiver(post_save, sender=Configuration)
def post_save_initialize(sender, instance, created, *args, **kwargs):
    if created:
        initialize_adherence.apply_async(
            kwargs = {
                'username': instance.user.username
            }
        )
