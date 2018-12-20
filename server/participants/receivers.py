from django.dispatch import receiver
from django.contrib.auth.models import User

from .signals import participant_enrolled
from .tasks import initialize_participant
from .models import Participant

@receiver(participant_enrolled, sender=User)
def async_initialize_participant(sender, username, *args, **kwargs):
    initialize_participant.apply_async(kwargs={
        'username': username
    })
