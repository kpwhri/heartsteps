# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from datetime import timedelta, datetime
from django.utils import timezone

from django.contrib.auth.models import User
from activity_suggestions.models import SuggestionTime

from randomization.models import Decision
from randomization.services import DecisionService, DecisionMessageService
from randomization.factories import make_decision_message

import pytz

def is_weekday_in_timezone(timezone):
    tz = pytz.timezone(timezone)
    dt = datetime.now()
    offset_dt = dt + dt.utcoffset(tz)

    weekday = offset_dt.weekday()
    if weekday >= 5:
        return False
    else:
        return True

@shared_task
def start_decision(username, time_category):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    decision_time = timezone.now() + timedelta(minutes=10)
    decision_service = DecisionService.create_decision(
        user = user,
        time = decision_time
    )
    decision_service.add_context("activity suggestion")
    decision_service.add_context(time_category)

    try:
        suggestion_time = SuggestionTime.objects.get(user=user, type=time_category)
        if is_weekday_in_timezone(suggestion_time.timezone):
            decision_service.add_context("weekday")
        else:
            decision_service.add_context("weekend")        
    except:
        pass

    decision_service.request_context()

    make_decision.apply_async(kwargs={
        'decision_id': str(decision_service.decision.id)
    }, eta=decision_time)

@shared_task
def make_decision(decision_id):
    decision = Decision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision.add_location_context()

    decision.a_it = True
    decision.pi_it = 1
    decision.save()

    decision_message_service = DecisionMessageService(decision)
    decision_message_service.make_message()
    decision_message_service.send_message()
