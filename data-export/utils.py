import os, sys, code
import pandas as pd
import progressbar
import pytz
import numpy as np
from datetime import datetime,  date, timedelta, timezone
from math import floor
import yaml

def read_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def setup():

    config        = read_config()
    EXPORT_DIR    = config["EXPORT_DIR"] 
    DATABASE_URL  = config["DATABASE_URL"]
    HS_SERVER_DIR = os.path.expanduser(config["HS_SERVER_DIR"]) 

    os.environ["DATABASE_URL"] = DATABASE_URL

    print(f"Export Configuration - EXPORT_DIR: {EXPORT_DIR}")
    print(f"Export Configuration - HS_SERVER_DIR: {HS_SERVER_DIR}")
    print(f"Export Configuration - DATABASE_URL: {DATABASE_URL}")
    print()

    sys.path.append(HS_SERVER_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

    from django.conf import settings
    import django
    django.setup()

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

def join_times(x):
    startdf = pd.DataFrame({'time':x['start'], 'what':1})
    enddf = pd.DataFrame({'time':x['end'], 'what':-1})
    mergdf = pd.concat([startdf, enddf]).sort_values('time')
    mergdf['running'] = mergdf['what'].cumsum()
    mergdf['newwin'] = mergdf['running'].eq(1) & mergdf['what'].eq(1)
    mergdf['group'] = mergdf['newwin'].cumsum()
    x['group'] = mergdf['group'].loc[mergdf['what'].eq(1)]
    res = x.groupby('group').agg({'start':min, 'end':max})
    res["duration"] = res["end"] - res["start"]
    res["date"] = res["start"].apply(lambda x: x.date())
    return res

def get_field_map(dictionary):
    final_field_name = dictionary["ElementName"]
    raw_field_name   = dictionary["Aliases"]  
    field_map={}
    for i in range(len(raw_field_name)):
        if(type(raw_field_name[i])!=str):
            field_map[final_field_name[i]]=final_field_name[i]
        else:
            field_map[raw_field_name[i]]=final_field_name[i]
    return  field_map

def setup_export_directory(export_dir):
    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)

if __name__ == "__main__":
    print("Found user IDs:",get_user_ids())
    print("Found users:",get_users())


def estimate_notification_dwell_times(user):
    allPageViews=PageView.objects.filter(user_id=user).order_by("created").all()
    notification_pages = [x for x in allPageViews  if "/notification/" in x.uri or "/dashboard" in x.uri]
    lookup = {}
    for i,n in enumerate(notification_pages):
        if("/notification/" in n.uri):
            nid = n.uri.split("/")[2]
            time_opened = n.created
            if(i<len(notification_pages)-1):
                if("/home/dashboard" in notification_pages[i+1].uri):
                    time_closed = notification_pages[i+1].created
                else:
                    time_closed=np.nan
            lookup[nid] = {"opened":time_opened,"closed":time_closed}
    return(lookup)

def estimate_survey_dwell_times(user,survey_type="weekly"):

    if(survey_type not in ["morning", "weekly"]):
        raise ValueError("Survey type must be morning or weekly")

    days = Day.objects.filter(user_id=user).order_by("date").all()
    allPageViews=PageView.objects.filter(user_id=user).order_by("created").all()
    survey_pages = [x for x in allPageViews  if f"/{survey_type}-survey/survey"== x.uri or "/dashboard" in x.uri]
    lookup = {}
    
    for i,x in enumerate(survey_pages):
        if("survey" in x.uri):
            time_opened = x.created
            this_day = days.filter(start__lte=time_opened).filter(end__gte=time_opened)
            time_opened_localized = this_day[0].localize(time_opened).time()
            date_localized        = this_day[0].localize(time_opened).date()
            if(i<len(survey_pages)-1):
                if("/home/dashboard" in survey_pages[i+1].uri):
                    time_closed = survey_pages[i+1].created
                    this_day = days.filter(start__lte=time_closed).filter(end__gte=time_closed)
                    time_closed_localized = this_day[0].localize(time_closed).time()
                else:
                    time_closed=None
                    time_closed_localized=None
            lookup[date_localized] = {"opened":time_opened,"closed":time_closed,"opened_localized":time_opened_localized,"closed_localized":time_closed_localized}
    
    return(lookup)



