import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone

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


def export_weekly_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    
    dictionary       = pd.read_csv("data_dictionaries/weekly.csv")
    final_field_name = dictionary["ElementName"]
    raw_field_name   = dictionary["Aliases"]
    field_map        = utils.get_field_map(dictionary)
    
    uid = user["uid"]
    username = user["hsid"]
    
    if(DEBUG):
        print("  Exporting weekly data for: ", username)
    
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
            dedup_time_df      = utils.join_times(raw_time_df.copy())
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
    
    if(DEBUG):
        print("    Wrote %d rows"%(len(df_all_fields)))
    