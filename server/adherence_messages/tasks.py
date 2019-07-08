from celery import shared_task

from .services import DailyAdherenceService

@shared_task
def update_adherence(username):
    service = DailyAdherenceService(username=username)
    service.update_adherence()
