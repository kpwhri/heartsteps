import os, sys
sys.path.append('/server')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

from django.conf import settings
import django
django.setup()

#import shutil
#import subprocess
#import csv
from datetime import datetime,  date, timedelta
from math import floor

#from celery import shared_task
from django.utils import timezone
#from django.conf import settings
#from django.core import serializers

#from adherence_messages.tasks import export_daily_metrics
#from anti_sedentary.tasks import export_anti_sedentary_decisions
#from anti_sedentary.tasks import export_anti_sedentary_service_requests
from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
#from fitbit_activities.tasks import export_fitbit_data
#from fitbit_activities.tasks import export_missing_fitbit_data
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Location
from locations.models import Place
#from locations.services import LocationService
#from locations.tasks import export_location_count_csv
#from locations.tasks import update_location_categories
#from morning_messages.tasks import export_morning_message_survey
#from morning_messages.tasks import export_morning_messages
from push_messages.models import Message as PushMessage
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
#from walking_suggestions.tasks import export_walking_suggestion_decisions
#from walking_suggestions.tasks import export_walking_suggestion_service_requests
#from watch_app.tasks import export_step_count_records_csv
from weekly_reflection.models import ReflectionTime

from participants.services import ParticipantService
from participants.models import Cohort
from participants.models import DataExport
from participants.models import DataExportSummary
from participants.models import DataExportQueue
from participants.models import Study
from participants.models import Participant

import pandas as pd
import progressbar
import pytz
import numpy as np

EXPORT_DIRECTORY = '/server/data_export/output' 

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
        users[hsid]={}
        users[hsid]["hsid"]=hsid
        users[hsid]["uid"] = p.user_id
        users[hsid]["fbid"] = FitbitAccountUser.objects.get(user_id=users[hsid]["uid"]).account_id
    return users
    
from fitbit_api.models import FitbitAccountUser

def setup_export_directory(export_dir):
    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)

def export_all_data(export_dir):
    setup_export_directory(EXPORT_DIRECTORY)
    
    users = get_users()
    
    for u in progressbar.progressbar(users):
    #for u in users:
        user_export_directory = os.path.join(EXPORT_DIRECTORY, u)
        setup_export_directory(user_export_directory)
        
        export_fitbit_minute_data(users[u], directory = user_export_directory)
        
        
def export_fitbit_minute_data(user, directory = None, filename = None, start=None, end=None):

    fitbit_account = user["fbid"]
    username = user["hsid"]

    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.fitbit-data-per-minute.csv'.format(
            username = username
        )
     
    #Get steps data
    query    = FitbitMinuteStepCount.objects.filter(account=fitbit_account).all().values('time','steps')
    df_steps = pd.DataFrame.from_records(query)
    df_steps = df_steps.rename(columns={"time":"datetime"}, )
    df_steps = df_steps.set_index("datetime")
    df_steps = df_steps.loc[~df_steps.index.duplicated()] #drop any duplicated index values

    #Get heart rate data
    query    = FitbitMinuteHeartRate.objects.filter(account=fitbit_account).all().values('time','heart_rate')
    df_hr    = pd.DataFrame.from_records(query)
    df_hr    = df_hr.rename(columns={"time":"datetime"}, )
    df_hr    = df_hr.set_index("datetime")
    df_hr    = df_hr.loc[~df_hr.index.duplicated()] #drop any duplicated index values

    #Get timezonedata
    query    = FitbitDay.objects.filter(account=fitbit_account).all().values('date','_timezone')
    df_tz    = pd.DataFrame.from_records(query)
    df_tz    = df_tz.rename(columns={"date":"datetime", "_timezone":"timezone"}, )
    df_tz['datetime'] = pd.to_datetime(df_tz['datetime'], utc=True)
    df_tz    = df_tz.set_index("datetime")

    #Trim days from start of timezone data where there is no fitbit data
    min_time = pd.to_datetime(max(df_hr.index[0].date(), df_steps.index[0].date()),utc=True)
    df_tz    = df_tz[df_tz.index>=min_time]

    #Extend timezone data to one day beyond last day of minute level data
    #Resample timezone data to minute level with forward fill 
    max_time = pd.to_datetime(max(df_hr.index[-1].date(), df_steps.index[-1].date()),utc=True)
    df_tz.loc[max_time+timedelta(days=1)] = df_tz.loc[df_tz.index[-1]]["timezone"]
    df_tz    = df_tz.resample('1Min').ffill()
    df_tz    = df_tz.drop(index=df_tz.index[-1]) #Drop last row so we end at 11:59pm
    df_tz    = df_tz.loc[~df_tz.index.duplicated()] #drop any duplicated index values

    #Join all datafames and set index
    df      = pd.concat([df_tz,df_steps,df_hr],axis=1,join="outer")
    df["Subject ID"]=username
    df      = df.reset_index().set_index(["Subject ID", "datetime"])

    #Set missing steps to 0 when HR is defined
    df['steps'] = df['steps'].fillna(0) #Set all missing steps to 0
    df.loc[df['heart_rate'].isnull(), 'steps'] = np.nan #Reset to nan when hr is null

    #Export to csv
    df.to_csv(os.path.join(directory,filename))

    #import code
    #code.interact(local=locals())


export_all_data(EXPORT_DIRECTORY)