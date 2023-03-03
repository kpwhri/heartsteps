import os, sys, code
import pandas as pd
import progressbar
import pytz
import numpy as np
from datetime import datetime,  date, timedelta, timezone
from math import floor

def setup():

    EXPORT_DIR    = os.environ["EXPORT_DIR"] 
    HS_SERVER_DIR = os.environ["HS_SERVER_DIR"] 
    DEBUG         = False

    print(f"Configuration - EXPORT_DIR: {EXPORT_DIR}")
    print(f"Configuration - HS_SERVER_DIR: {EXPORT_DIR}")

    sys.path.append(HS_SERVER_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

    from django.conf import settings
    import django
    django.setup()

#Must all setup before importing django modules
setup()


from django.utils import timezone
from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.models import FitbitActivity

from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Location
from locations.models import Place
from push_messages.models import Message as PushMessage
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from weekly_reflection.models import ReflectionTime

from participants.services import ParticipantService
from participants.models import Cohort
from participants.models import DataExport
from participants.models import DataExportSummary
from participants.models import DataExportQueue
from participants.models import Study
from participants.models import Participant

from weeks.models import Week
from surveys.models import Survey
from page_views.models import PageView
from activity_plans.models import  ActivityPlan
from activity_logs.models import ActivityLog


def format_datetime(dt, tz=None):
    if dt:
        if tz:
            dt = dt.astimezone(tz)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None

def get_user_ids():
    participants = Participant.objects.all()
    ids = [p.user_id for p in participants if p.user_id]
    return(ids)
    
def get_hs_ids():
    participants = Participant.objects.all()
    ids = [p.heartsteps_id for p in participants]
    return(ids)


def get_users():
    participants = Participant.objects.all()
    users ={}
    for p in participants:
        hsid = p.heartsteps_id
        if (hsid is None): continue
        
        uid  = p.user_id
        if (uid is None): continue
        
        try:
            fbid = FitbitAccountUser.objects.get(user_id=uid).account_id
            users[hsid]={}
            users[hsid]["hsid"]=hsid
            users[hsid]["uid"] = uid
            users[hsid]["fbid"] = fbid
            users[hsid]["cohort"] = p.cohort.name
            
        except FitbitAccountUser.DoesNotExist:
            pass

    return users


print("Found user IDs:",get_user_ids())
print("Found user IDs:",get_users())