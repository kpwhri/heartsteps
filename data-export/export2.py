EXPORT_DIRECTORY = '/data-export/output' 
DEBUG = False

import os, sys, code
sys.path.append('/server')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

from django.conf import settings
import django
django.setup()

#import shutil
#import subprocess
#import csv
from datetime import datetime,  date, timedelta, timezone
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
from fitbit_activities.models import FitbitActivity

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

from weeks.models import Week
from surveys.models import Survey
from page_views.models import PageView
from activity_plans.models import  ActivityPlan
from activity_logs.models import ActivityLog

import pandas as pd
import progressbar
import pytz
import numpy as np



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
    
from fitbit_api.models import FitbitAccountUser

def setup_export_directory(export_dir):
    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)

def export_all_data(export_dir, cohort="U01"):
    
    print("Starting data export")
    
    setup_export_directory(EXPORT_DIRECTORY)
    users = get_users()
    
    count=0
    for u in progressbar.progressbar(users):
    #for u in users:
        try:
            if(users[u]["cohort"]!=cohort): continue
            user_export_directory = os.path.join(EXPORT_DIRECTORY, users[u]["cohort"], u)
            setup_export_directory(user_export_directory)
        
            #export_fitbit_minute_data(users[u], directory = user_export_directory)        
            export_weekly_data(users[u], directory = user_export_directory, from_scratch=False)
            
        except Exception as e:
            print("Error exporting data for user: " + u)
            print(e)

        if(DEBUG==True and count>=5):
            break        
        count=count+1


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

def export_weekly_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True):
    
    dictionary       = pd.read_csv("data_dictionaries/weekly.csv")
    final_field_name = dictionary["ElementName"]
    raw_field_name   = dictionary["Aliases"]
    field_map        = get_field_map(dictionary)
    
    uid = user["uid"]
    username = user["hsid"]
    
    if(DEBUG):
        print("Exporting weekly data for: ", username)
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.weekly_planning.csv'.format(
            username = username
        )
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    def safe_list_to_str(opts):
        if opts is not None:
            return ",".join(opts)
        else: 
            return np.nan 
    
    week_query = Week.objects.filter(user=uid).all().values('number','start_date','end_date','goal','confidence','survey_id')
    df_week = pd.DataFrame.from_records(week_query)
    df_week = df_week.set_index("number")
    df_week = df_week.drop(columns=['survey_id'])
    
    answers=[]
    barriers=[]
    planning=[]
    activities=[]
    weeks = Week.objects.filter(user=uid).all()
    
    for week in weeks:
        survey_query = Survey.objects.filter(uuid = week.survey_id).all()
        if(len(survey_query)>0):
            answer = survey_query[0].get_answers()
            answer["number"]=week.number          
            answers.append(answer)
        
        #midnight on first day of week
        activity_interval_start = datetime(week.start_date.year, week.start_date.month, week.start_date.day,0,0,0,tzinfo=timezone.utc)
        #noon on last day of the previous week
        planning_interval_start = activity_interval_start - timedelta(hours=12)
        #23:59:59 on last day of week
        interval_end            = datetime(week.end_date.year, week.end_date.month, week.end_date.day,23,59,59,tzinfo=timezone.utc)
        
        plans = ActivityPlan.objects.filter(user_id=uid)\
                                    .filter(created_at__range=(planning_interval_start, interval_end))\
                                    .filter(start__range=(activity_interval_start, interval_end))\
        
        plan_info = {"number":week.number}
        if(len(plans)>0):
            plan_info["made_plan"]=True
            plan_info["number_of_days_with_planning"] = len(np.unique([p.created_at.date() for p in plans]))
            plan_info["number_of_days_with_planned_activities"] = len(np.unique([p.start.date() for p in plans]))
            plan_info["number_of_planned_activities"] = len(plans)
            plan_info["duration_of_planned_activities"] = np.sum([p.duration for p in plans])
            plan_info["number_of_planned_activities_marked_completed"] = len([p for p in plans if p.activity_log_id is not None])
            plan_info["duration_of_planned_activities_marked_completed"] = np.sum([p.duration for p in plans if p.activity_log_id is not None])
        else:
            plan_info["made_plan"]=False
            plan_info["number_of_days_with_planning"]=0
            plan_info["number_of_days_with_planned_activities"]=0
            plan_info["number_of_planned_activities"]=0
            plan_info["duration_of_planned_activities"]=0
            plan_info["number_of_planned_activities_marked_completed"] = 0
            plan_info["duration_of_planned_activities_marked_completed"] =0
        planning.append(plan_info)
        
        activity_info = {"number":week.number}
        
        #Use all activities
        #activity_log = ActivityLog.objects.filter(user_id=uid)\
        #                            .filter(start__range=(activity_interval_start, interval_end))
         
        #Only use fitbit activities                            
        activity_log = FitbitActivity.objects.filter(account_id=user["fbid"])\
                                    .filter(start_time__range=(activity_interval_start, interval_end))
        
        if(len(activity_log)>0):
                        
            activity_info["number_of_activity_bouts"] = len(activity_log)

            #Get raw activity duriation sum with overlaps    
            raw_duration_sum = np.sum([a.duration for a in activity_log])

            #Filter overlapping activities
            raw_time_df       = pd.DataFrame([[a.start_time, a.end_time] for a in activity_log], columns=["start","end"])
            dedup_time_df      = join_times(raw_time_df.copy())
            dedup_duration_sum = dedup_time_df["duration"].sum().seconds/60
            activity_info["duration_of_activity_bouts"] = dedup_duration_sum

            if(len(plans)>0):
                dates_with_plan = np.unique([p.start.date() for p in plans])
                activity_info["duration_of_activity_bouts_on_plan_days"] = dedup_time_df[dedup_time_df["date"].isin(dates_with_plan)]["duration"].sum().seconds/60

                dates_with_completed_plan = list(np.unique([p.start.date() for p in plans if p.activity_log_id is not None]))
                if(len(dates_with_completed_plan)>0):
                    activity_info["duration_of_activity_bouts_on_marked_completed_plan_days"] = dedup_time_df[dedup_time_df["date"].isin(dates_with_completed_plan)]["duration"].sum().seconds/60
                else:
                    activity_info["duration_of_activity_bouts_on_marked_completed_plan_days"] = 0
            else:
                activity_info["duration_of_activity_bouts_on_plan_days"] = 0
                activity_info["duration_of_activity_bouts_on_marked_completed_plan_days"] = 0


            #Print activity checks
            '''if(np.abs(raw_duration_sum - dedup_duration_sum )>1):
                print("Duration gap. Raw: %.2f  Dedup: %.2f"%(raw_duration_sum,dedup_duration_sum))
                print(raw_time_df)
                print(dedup_time_df )'''
            
        else:
            activity_info["number_of_activity_bouts"] = 0
            activity_info["duration_of_activity_bouts"] = 0
            activity_info["duration_of_activity_bouts_on_plan_days"]=0
            activity_info["duration_of_activity_bouts_on_marked_completed_plan_days"] = 0

        activities.append(activity_info)

        #import code
        #code.interact(local=dict(globals(), **locals()))

        barriers.append({"number":week.number, "barriers": safe_list_to_str(week.barriers)})
        
    df_answers = pd.DataFrame(answers)
    df_answers = df_answers.set_index("number")

    df_planning = pd.DataFrame(planning)
    df_planning = df_planning.set_index("number")
    
    df_activities = pd.DataFrame(activities)
    df_activities = df_activities.set_index("number")
    
    df_barriers = pd.DataFrame(barriers)
    df_barriers= df_barriers.set_index("number")

    df = df_week.join(df_answers).join(df_barriers).join(df_planning).join(df_activities)
    df["Subject ID"]=username
    
    df_empty = pd.DataFrame(columns = raw_field_name)
    df_empty = df_empty.set_index("number")
    
    df_all_fields = pd.concat([df_empty, df])
    df_all_fields = df_all_fields.reset_index()
    df_all_fields = df_all_fields.rename(columns=field_map)
    df_all_fields = df_all_fields.set_index(["Subject ID", "study_week"])
    df_all_fields.to_csv(os.path.join(directory,filename))
    
    print(df_all_fields)
    
    return df
    
    

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



export_all_data(EXPORT_DIRECTORY, cohort='Aim 3')