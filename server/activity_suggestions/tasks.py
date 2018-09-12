# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from datetime import timedelta, datetime
from django.utils import timezone

from django.contrib.auth.models import User
from activity_suggestions.models import SuggestionTime
from randomization.models import Decision
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

    decision = Decision.objects.create(
        user = user,
        time = decision_time
    )
    decision.add_context("activity suggestion")
    decision.add_context(time_category)

    try:
        suggestion_time = SuggestionTime.objects.get(user=user, type=time_category)
        if is_weekday_in_timezone(suggestion_time.timezone):
            decision.add_context("weekday")
        else:
            decision.add_context("weekend")        
    except:
        pass

    decision.get_context()

    make_decision.s(str(decision.id)).apply_async(eta=decision_time)

@shared_task
def make_decision(decision_id):
    decision = Decision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision.add_location_context()

    decision.a_it = True
    decision.pi_it = 1
    decision.save()

    message = make_decision_message(decision)
    message.send_message()
