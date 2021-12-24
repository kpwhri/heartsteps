import os
from participants.models import Participant
import pytz
import json
import random
from celery import shared_task
from datetime import timedelta, datetime, date
import requests
from daily_step_goals.models import StepGoalsEvidence, User
from user_event_logs.models import EventLog

import daily_step_goals.services
import fitbit_api.services
from days.services import DayService

@shared_task
def update_goal(username):
    # dt = datetime.strptime(day_string, '%Y-%m-%d')
    # day = date(dt.year, dt.month, dt.day)
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    
    user = User.objects.get(username=username)
    participant = Participant.objects.get(user=user)
    enrollment_date = participant.study_start_date
    day_service = DayService(user)
    today = day_service.get_current_date()

    stepgoal_service = daily_step_goals.services.StepGoalsService(user)

    
    query = StepGoalsEvidence.objects.filter(user=user, startdate__lte=today, enddate__gte=today).order_by('-created')
    
    if not query.exists():
        # no calculation evidence is found
        last_evidence_query = StepGoalsEvidence.objects.filter(user=user).order_by('-enddate', '-created')
        if not last_evidence_query.exists():
            # no evidence is found at all
            startdate = enrollment_date
        else:
            # some evidence is found
            last_evidence = last_evidence_query.first()
            if last_evidence.enddate > today:
                # calculation is completely wrong. re-calculating from the start
                enrollment_date = participant.study_start_date
                startdate = enrollment_date
            else:
                # calculation stopped sometime before
                startdate = last_evidence.enddate + timedelta(days=1)            
        while startdate <= today:
            evidence = stepgoal_service.calculate_step_goals(startdate=startdate)
            startdate = evidence.enddate + timedelta(days=1)
    else:
        # this query is called repeatedly even there is an evidence that covers today.
        # recalculating and if it doesn't match with the previous records, we keep history.
        evidence_for_today = query.first()
        startdate = evidence_for_today.startdate
        
        stepgoal_service.calculate_step_goals(startdate=startdate)
                
    step_goal = stepgoal_service.get_goal(today)
    
    
    update_fitbit_device_with_new_goal(user, step_goal)

def update_fitbit_device_with_new_goal(user, step_goal):
    fitbit_service = fitbit_api.services.FitbitClient(user)
    
    fitbit_service.update_step_goals(step_goal)
