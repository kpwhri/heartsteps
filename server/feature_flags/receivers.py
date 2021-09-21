from django.dispatch import receiver
from django.db.models.signals import post_save
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