from celery import shared_task

from .services import AdherenceService

@shared_task
def initialize_adherence(username):
    service = AdherenceService(username=username)
    service.initialize()

@shared_task
def send_adherence_message(username):
    service = AdherenceService(username=username)
    service.send_adherence_message()

@shared_task
def update_adherence(username):
    service = AdherenceService(username=username)
    service.update_adherence()
