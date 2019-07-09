from celery import shared_task

from .services import AdherenceService

@shared_task
def update_adherence(username):
    service = AdherenceService(username=username)
    service.update_adherence()
