from django.dispatch import receiver

from walking_suggestion_times.signals import suggestion_times_updated

from .models import SuggestionTime, Configuration

@receiver(suggestion_times_updated, sender=SuggestionTime)
def post_save_configuration(sender, username, *args, **kwargs):
    try:
        configuration = Configuration.objects.get(user__username=username)
    except Configuration.DoesNotExist:
        return False
    configuration.update_suggestion_times()
