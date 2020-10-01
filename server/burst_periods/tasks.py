from celery import shared_task

from days.services import DayService

from .models import Configuration

@shared_task
def update_burst_probability(username):
    try:
        configuration = Configuration.objects.get(
            user__username = username
        )
        service = DayService(username=username)
        today = service.get_current_date()
        configuration.update_randomization_probabilities(today)
    except Configuration.DoesNotExist:
        pass

