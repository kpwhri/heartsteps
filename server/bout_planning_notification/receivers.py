from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import FirstBoutPlanningTime
from user_event_logs.models import EventLog
from django.db.models import Model
import pprint

@receiver(post_save, sender=FirstBoutPlanningTime)
def FeatureFlags_updated(instance, created, **kwargs):
    if created:
        msg = "FirstBoutPlanningTime created: {}".format(instance)
    else:
        msg = "FirstBoutPlanningTime updated: {}".format(instance)
    EventLog.log(instance.user, msg, EventLog.INFO)