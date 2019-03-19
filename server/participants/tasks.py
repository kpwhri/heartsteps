from datetime import timedelta

from celery import shared_task

from .services import ParticipantService

@shared_task
def daily_update(username):
    service = ParticipantService(username=username)
    yesterday = service.get_current_datetime() - timedelta(days=1)
    service.update(yesterday)
