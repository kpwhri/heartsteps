from django.dispatch import receiver
from django.db.models.signals import pre_save

from weekly_reflection.signals import weekly_reflection

from .models import User, Week, WeekSurvey
from .tasks import send_reflection

@receiver(weekly_reflection, sender=User)
def send_weekly_reflection(sender, username, *args, **kwargs):
    send_reflection(username=username)
