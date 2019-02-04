from django.dispatch import receiver

from walking_suggestion_times.signals import suggestion_times_updated

from .models import SuggestionTime, Configuration, User
from .tasks import initialize_walking_suggestion_service

@receiver(suggestion_times_updated, sender=SuggestionTime)
def post_save_configuration(sender, username, *args, **kwargs):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    configuration, _ = Configuration.objects.get_or_create(user = user)
    configuration.update_suggestion_times()

    initialize_walking_suggestion_service.apply_async(kwargs={
        'username': username
    })
