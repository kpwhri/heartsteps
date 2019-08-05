from datetime import timedelta

from celery import shared_task

from days.services import DayService

from .services import ParticipantService

@shared_task
def daily_update(username):
    service = ParticipantService(username=username)
    day_service = DayService(username=username)
    yesterday = day_service.get_current_date() - timedelta(days=1)
    service.update(yesterday)
