from django.dispatch import receiver
from django.db.models.signals import post_save

from walking_suggestion_times.models import SuggestionTime
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from .services import AntiSedentaryService
from .models import User, Configuration
from .tasks import start_decision

@receiver(suggestion_times_updated, sender=User)
def suggestion_times_update(sender, username, *args, **kwargs):
    try:
        user = User.objects.get(username=username)
        Configuration.objects.update_or_create(
            user = user,
            defaults = {
                'enabled': True
            }
        )
    except User.DoesNotExist:
        pass

@receiver(step_count_updated, sender=User)
def step_count_update(sender, username, *args, **kwargs):
    start_decision.apply_async(kwargs = {
        'username': username
    })
