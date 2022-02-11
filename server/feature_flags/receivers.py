
# TODO: ASK WHAT THIS IMPORT IS INTENDED TO DO
# from msilib.schema import Feature

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

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

@receiver(pre_save, sender=FeatureFlags)
def adherence_message_check(instance, **kwargs):
    participant = Participant.objects.get(user=instance.user)
    print("HS DEBUG: participant: ", participant)
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
        # print("HS DEBUG: has flag adherence messages")
        if not participant.user:
            return
        config = AdherenceMessageConfiguration.objects.get(
            user=participant.user)
        config.enabled = True
        config.save()
        # print("DEBUG: configuration is enabled")
        # assert(is_configuration_enabled())
    
    # default behavior be to turn adherence messages off
    else:
        # print("HS DEBUG: does not have flag adherence messages")
        config, _ = AdherenceMessageConfiguration.objects.get_or_create(
            user=participant.user)
        config.enabled = False
        config.save()
        # print("DEBUG: configuration is enabled")
        # assert(not is_configuration_enabled())
