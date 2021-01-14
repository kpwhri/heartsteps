import os, sys
sys.path.append('/server')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

from django.conf import settings
import django
django.setup()

import shutil
import subprocess
import csv
from datetime import date
from datetime import timedelta
from math import floor

from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core import serializers

from adherence_messages.tasks import export_daily_metrics
from anti_sedentary.tasks import export_anti_sedentary_decisions
from anti_sedentary.tasks import export_anti_sedentary_service_requests
from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
#from fitbit_activities.tasks import export_fitbit_data
from fitbit_activities.tasks import export_missing_fitbit_data
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Location
from locations.models import Place
from locations.services import LocationService
from locations.tasks import export_location_count_csv
from locations.tasks import update_location_categories
from morning_messages.tasks import export_morning_message_survey
from morning_messages.tasks import export_morning_messages
from push_messages.models import Message as PushMessage
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.tasks import export_walking_suggestion_decisions
from walking_suggestions.tasks import export_walking_suggestion_service_requests
from watch_app.tasks import export_step_count_records_csv
from weekly_reflection.models import ReflectionTime

from participants.services import ParticipantService
from participants.models import Cohort
from participants.models import DataExport
from participants.models import DataExportSummary
from participants.models import DataExportQueue
from participants.models import Study
from participants.models import Participant

from datetime import datetime, timedelta
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
    
    #Get all steps data
    steps_data = FitbitMinuteStepCount.objects.filter(account=fitbit_account).all()    
    steps_data_by_time = {"datetime":[], "steps":[]}
    for rec in steps_data:
        steps_data_by_time["datetime"].append(rec.time)        
        steps_data_by_time["steps"].append(rec.steps)
    df_steps = pd.DataFrame(steps_data_by_time).set_index("datetime")
    df_steps = df_steps.loc[~df_steps.index.duplicated()] #drop any duplicated index values
    
    #Get all heart rate data
    hr_data   = FitbitMinuteHeartRate.objects.filter(account=fitbit_account).all()
    hr_data_by_time = {"datetime":[], "heart_rate":[]}
    for rec in hr_data:
        hr_data_by_time["datetime"].append(rec.time)        
        hr_data_by_time["heart_rate"].append(rec.heart_rate)
    df_hr = pd.DataFrame(hr_data_by_time).set_index("datetime")
    df_hr = df_hr.loc[~df_hr.index.duplicated()] #drop any duplicated index values

    #Get all days with data
    #Note: Should be possible to replace all of this logic with pandas time axis resampling    
    days_by_date = {}
    for fitbit_day in FitbitDay.objects.filter(account=fitbit_account).all():
        if start and start >= fitbit_day.get_end_datetime():
            continue
        if end and end <= fitbit_day.get_start_datetime():
            continue
        days_by_date[fitbit_day.date] = fitbit_day
    if not days_by_date:
        raise 'No fitbit days exist for user'
    dates = sorted(list(days_by_date.keys()))
    date_range = (dates[-1] - dates[0]).days
    all_days = [dates[0] + timedelta(days=offset) for offset in range(date_range)]

    #Enumerate all minutes in each day and create subject ID and timezone fields
    data ={}
    data["Subject ID"] = []
    data["timezone "] = []
    data["datetime"]=[]
    for _date in all_days:
        if _date in days_by_date:
            day = days_by_date[_date]
            #Use last known time zone if no data on a given day
            tz  = day._timezone
        start_datetime = datetime(_date.year, _date.month, _date.day, 0, 0, 0)
        end_datetime = start_datetime + timedelta(days=1)
        current_minute = start_datetime
        while current_minute < end_datetime:
            data["Subject ID"].append(username)
            data["timezone "].append(tz)
            #Need to make the current minute timezone aware
            data["datetime"].append(current_minute.replace(tzinfo=timezone.utc))
            current_minute = current_minute + timedelta(minutes=1)
    df_idtz = pd.DataFrame(data).set_index("datetime")
    df_idtz = df_idtz.loc[~df_idtz.index.duplicated()] #drop any duplicated index values

    #Combine the data frames using outer join
    #Will create missing fitbit data where none was found above
    df = pd.concat([df_idtz,df_steps,df_hr],axis=1,join="outer")
    df = df.reset_index().set_index(["Subject ID", "datetime"])
    
    #Set missing steps to 0 when HR is defined
    df['steps'] = df['steps'].fillna(0) #Set all missing steps to 0
    df.loc[df['heart_rate'].isnull(), 'steps'] = np.nan #Reset to nan when hr is null
    
    #Export to csv
    df.to_csv(os.path.join(directory,filename))

    #import code
    #code.interact(local=locals())
 
export_all_data(EXPORT_DIRECTORY)