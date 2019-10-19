from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

from walking_suggestion_times.models import SuggestionTime
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from .services import AntiSedentaryService
from .models import User
from .models import AntiSedentaryMessageTemplate
from .models import Configuration

@receiver(pre_save, sender=AntiSedentaryMessageTemplate)
def set_message_template_title(sender, instance, *args, **kwargs):
    if not instance.title:
        instance.title = "Been sitting for too long?"

