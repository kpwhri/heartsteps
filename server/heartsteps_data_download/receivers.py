from django.dispatch import receiver

from participants.models import User
from participants.signals import nightly_update

from .tasks import export_user_data

@receiver(nightly_update, sender=User)
def queue_data_download(sender, user, *args, **kwargs):
    export_user_data.apply_async(kwargs={
        'username': user.username
    })
