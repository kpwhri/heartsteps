from celery import shared_task

from days.services import DayService

from .models import Configuration

@shared_task
def update_burst_probability(username):
    pass
