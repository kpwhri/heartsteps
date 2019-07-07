from celery import shared_task

from days.services import DayService

from .models import Configuration
from .models import User
from .signals import update_adherence as update_adherence_signal

@shared_task
def update_adherence(username):
    configuration = Configuration.objects.get(user__username = username)
    if configuration.enabled:
        day_service = DayService(user = configuration.user)
        update_adherence_signal.send(
            sender = User,
            user = configuration.user,
            date = day_service.get_current_date()
        )
