from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

from participants.signals import nightly_update
from walking_suggestion_times.models import SuggestionTime
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from .services import AntiSedentaryService
from .models import User
from .models import AntiSedentaryMessageTemplate
from .models import Configuration
from .tasks import start_decision

@receiver(nightly_update, sender=User)
def update_anti_sedentary_service(user, day, *args, **kwargs):
    try:
        anti_sedentary_service = AntiSedentaryService(
            user = user
        )
        anti_sedentary_service.update(day)
    except (AntiSedentaryService.NoConfiguration, AntiSedentaryService.Unavailable):
        pass

@receiver(suggestion_times_updated, sender=User)
def suggestion_times_update(sender, username, *args, **kwargs):
    try:
        user = User.objects.get(username=username)
        Configuration.objects.update_or_create(
            user = user,
            defaults = {
                'enabled': True
            }
        )
    except User.DoesNotExist:
        pass

@receiver(step_count_updated, sender=User)
def step_count_update(sender, username, *args, **kwargs):
    start_decision.apply_async(kwargs = {
        'username': username
    })

@receiver(pre_save, sender=AntiSedentaryMessageTemplate)
def set_message_template_title(sender, instance, *args, **kwargs):
    if not instance.title:
        instance.title = "Been sitting for too long?"

