from datetime import timedelta

from django.utils import timezone

from celery import shared_task

from .services import WeekService

@shared_task
def send_reflection(username):
    service = WeekService(username=username)
    week = service.get_current_week()
    service.send_reflection(week)        
