from celery import shared_task

from days.services import DayService

from .models import Configuration

@shared_task
def update_burst_probability(username):
    try:
        configuration = Configuration.objects.get(
            user__username = username
        )
        configuration.set_current_intervention_configuration()
    except Configuration.DoesNotExist:
        pass

