from django.dispatch import receiver

from walking_suggestion_times.signals import suggestion_times_updated

from .models import Configuration
from .models import User

@receiver(suggestion_times_updated, sender=User)
def update_walking_suggestion_survey_times(sender, username, *args, **kwargs):
    try:
        configuration = Configuration.objects.get(
            user__username=username
        )
        configuration.update_survey_times()
    except Configuration.DoesNotExist:
        pass
