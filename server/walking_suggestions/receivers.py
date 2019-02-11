from django.dispatch import receiver

from walking_suggestion_times.signals import suggestion_times_updated

from .models import SuggestionTime, Configuration, User

@receiver(suggestion_times_updated, sender=SuggestionTime)
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
    configuration.update_suggestion_times()
