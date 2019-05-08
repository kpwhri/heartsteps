from django.dispatch import receiver

from participants.signals import nightly_update as participant_nightly_update
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from .models import SuggestionTime, Configuration, User
from .tasks import create_decision, nightly_update

@receiver(suggestion_times_updated, sender=User)
def post_save_configuration(sender, username, *args, **kwargs):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    configuration, _ = Configuration.objects.update_or_create(
        user = user,
        defaults = {
            'enabled': True
        }
    )

@receiver(step_count_updated, sender=User)
def step_count_update(sender, username, *args, **kwargs):
    create_decision.apply_async(kwargs = {
        'username': username
    })

@receiver(participant_nightly_update, sender=User)
def queue_nightly_update(sender, user, day, *args, **kwargs):
    nightly_update.apply_async(kwargs={
        'username': user.username,
        'day_string': day.strftime('%Y-%m-%d')
    })
