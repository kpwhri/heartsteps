from django.dispatch import receiver

from watch_app.models import User
from watch_app.signals import step_count_updated

from .tasks import step_count_message_randomization

@receiver(step_count_updated, sender=User)
def step_count_update(sender, username, *args, **kwargs):
    step_count_message_randomization.apply_async(kwargs = {
        'username': username
    })
