from django.dispatch import receiver
from django.db.models.signals import post_save

from anti_seds.models import StepCount
from walking_suggestion_times.models import SuggestionTime
from walking_suggestion_times.signals import suggestion_times_updated

from .services import AntiSedentaryService
from .tasks import start_decision

@receiver(suggestion_times_updated, sender=SuggestionTime)
def suggestion_times_update(sender, username, *args, **kwargs):
    try:
        service = AntiSedentaryService(username=username)
        service.enable()
    except:
        pass

@receiver(post_save, sender=StepCount)
def step_count_update(sender, instance, *args, **kwargs):
    start_decision.apply_async(kwargs = {
        'username': instance.user.username
    })
