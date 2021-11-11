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
from fitbit_api.services import FitbitClient

@shared_task
def update_goal(username):
    # dt = datetime.strptime(day_string, '%Y-%m-%d')
    # day = date(dt.year, dt.month, dt.day)
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    try:
        service = StepGoalsService()
        fitbit_service = FitbitClient()
        user = User.objects.get(username=username)
        from days.services import DayService
        day_service = DayService(user)
        today = day_service.get_current_date()
        service.create(today)
        fitbit_service.update_step_goal()
    except StepGoalsService.NotEnabled():
        return None
