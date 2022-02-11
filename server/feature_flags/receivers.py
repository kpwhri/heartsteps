from msilib.schema import Feature
from django.dispatch import receiver
from django.db.models.signals import post_save

from participants.models import Participant
from adherence_messages.models import Configuration as AdherenceMessageConfiguration
from .models import FeatureFlags
from user_event_logs.models import EventLog
import pprint

@receiver(post_save, sender=FeatureFlags)
def FeatureFlags_updated(instance, created, **kwargs):
    if created:
        msg = "FeatureFlags created: {}".format(instance.flags)
    else:
        msg = "FeatureFlags updated: {}".format(instance.flags)
    EventLog.log(instance.user, msg, EventLog.INFO)

@receiver(post_save, sender=FeatureFlags)
def adherence_message_check(instance, created, **kwargs):
    participant = Participant.objects.get(user=instance.user)
    # config = AdherenceMessageConfiguration.objects.get(user=participant.user)

    def is_configuration_enabled():
        if not participant.user:
            return False
        try:
            configuration = AdherenceMessageConfiguration.objects.get(
                user=participant.user)
            return configuration.enabled
        except AdherenceMessageConfiguration.DoesNotExist:
            return False
    
    if instance.has_flag("adherence_messages"):
        if not participant.user:
            return
        if is_configuration_enabled():
            config = AdherenceMessageConfiguration.objects.get(
                user=participant.user)
            config.enabled = True
            config.save()
    
    # default behavior be to turn adherence messages off
    else:
        config, _ = AdherenceMessageConfiguration.objects.get_or_create(
            user=participant.user)
        config.enabled = False
        config.save()