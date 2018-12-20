from celery import shared_task

from morning_messages.services import MorningMessageDecisionService

@shared_task
def send_morning_message(username):
    service = MorningMessageDecisionService(username=username)
    service.send_message()
