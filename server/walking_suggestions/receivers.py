from django.dispatch import receiver
from django.db.models.signals import pre_save

from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from .models import Configuration
from .models import SuggestionTime
from .models import User
from .models import WalkingSuggestionMessageTemplate

@receiver(pre_save, sender=WalkingSuggestionMessageTemplate)
def set_message_template_title(sender, instance, *args, **kwargs):
    if not instance.title:
        instance.title = "Time for a quick walk?"
