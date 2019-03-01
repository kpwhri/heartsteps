from celery import shared_task
from datetime import timedelta, datetime

from push_messages.services import PushMessageService
from weeks.services import WeekService

@shared_task
def send_reflection(username):
    week_service = WeekService(username=username)
    current_week = week_service.get_current_week()
    next_week = week_service.get_week_after(current_week)

    push_service = PushMessageService(username=username)
    push_service.send_data({
        'type': 'weekly-reflection',
        'weekId': current_week.number
    })    
