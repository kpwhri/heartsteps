from celery import shared_task
from datetime import timedelta, datetime

from push_messages.services import PushMessageService
from weeks.services import WeekService

@shared_task
def send_reflection(username):
    week_service = WeekService(username=username)
    current_week = week_service.get_current_week()

    next_week_start = current_week.end_date + timedelta(days=1)
    try:
        next_week = week_service.get_week_for_date(next_week_start)
    except WeekService.WeekDoesNotExist:
        next_week = week_service.create_week(
            start_date = next_week_start
        )

    push_service = PushMessageService(username=username)
    push_service.send_notification(
        body = "Time for weekly reflection",
        data = {
            'type': 'weekly reflection',
            'week': {
                'id': current_week.number,
                'start': current_week.start_date.strftime('%Y-%m-%d'),
                'end': current_week.end_date.strftime('%Y-%m-%d')
            }
        }
    )    
