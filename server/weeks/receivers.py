from django.dispatch import receiver
from django.db.models.signals import pre_save

from weekly_reflection.signals import weekly_reflection

from .models import User, Week
from .tasks import send_reflection

@receiver(pre_save, sender=Week)
def set_week_number(sender, instance, *args, **kwargs):
    if instance.number is None:
        number_of_weeks = Week.objects.filter(user=instance.user).count()
        instance.number = number_of_weeks + 1

@receiver(pre_save, sender=Week)
def set_week_goal(sender, instance, *args, **kwargs):
    if not instance.goal:
        instance.goal = instance.get_default_goal()


@receiver(weekly_reflection, sender=User)
def send_weekly_reflection(sender, username, *args, **kwargs):
    send_reflection(username=username)
