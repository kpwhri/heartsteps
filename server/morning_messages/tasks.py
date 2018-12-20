from celery import shared_task

from morning_messages.services import MorningMessageService

@shared_task
def send_morning_message(username):
    service = MorningMessageService(username=username)
    service.send_message()
