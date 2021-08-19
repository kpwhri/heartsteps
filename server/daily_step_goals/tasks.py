import os
import pytz
import json
import random
from celery import shared_task
from datetime import timedelta, datetime, date
import requests
from .models import User
from user_event_logs.models import EventLog

from .services import StepGoalsService

@shared_task
def update_goal():
    # dt = datetime.strptime(day_string, '%Y-%m-%d')
    # day = date(dt.year, dt.month, dt.day)
    try:
        service = StepGoalsService()
        service.create(date.today())
    except StepGoalsService.NotEnabled():
        return None
