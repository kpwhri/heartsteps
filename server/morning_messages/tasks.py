from datetime import date

from celery import shared_task

from morning_messages.services import MorningMessageService

@shared_task
def send_morning_message(username):
    service = MorningMessageService(username=username)
    try:
        service.send_notification(date.today())
    except MorningMessageService.NotEnabled:
        pass
