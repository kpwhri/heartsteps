from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import SuggestionTime, Configuration

@receiver(post_save, sender=SuggestionTime)
def post_save_configuration(sender, instance, *args, **kwargs):
    instance.update_daily_task()
