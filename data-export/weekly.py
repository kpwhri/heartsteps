import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone

from fitbit_activities.models import FitbitActivity
from weeks.models import Week
from surveys.models import Survey
from activity_plans.models import  ActivityPlan
from days.models import Day

def export_weekly_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    
    dictionary       = pd.read_csv("data_dictionaries/weekly.csv")
    final_field_name = dictionary["ElementName"]
    raw_field_name   = dictionary["Aliases"]
    field_map        = utils.get_field_map(dictionary)
    
    uid = user["uid"]
    username = user["hsid"]
    
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
    
    print("  Wrote %d rows"%(len(df_all_fields)))
    
def export_weekly_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    
    dictionary       = pd.read_csv("data_dictionaries/weekly.csv")
    final_field_name = dictionary["ElementName"]
    raw_field_name   = dictionary["Aliases"]
    field_map        = utils.get_field_map(dictionary)
    
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.weekly_survey.csv'.format(
            username = username
        )
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return

    #Query weeks object    
    week_query = Week.objects.filter(user=uid).all()
    df = pd.DataFrame({'Object': [w for w in week_query]})

    #Map base fields
    base_fields = {'number':"Study Week",
                'start_date':"Start Date",
                'end_date':"End Date",
                'goal':"Activity Goal",
                'confidence':"Activity Goal Confidence",
                '_barrier_options':"Barriers",
                'will_barriers_continue':"Will Barriers Continue"
                'answered'}
    for f,n in base_fields.items():
        df[n]=df["Object"].map(lambda x: getattr(x,f))

    #Re-map barriers list to string with : separator
    #There is not a fixed list of barriers
    df["Barriers"]=df["Barriers"].map(lambda x: ":".join(x) if x is not None else None)

    #Get survey indicators

    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}
    sdt       = utils.estimate_survey_dwell_times(uid,survey_type="weekly")

    wsot=df["Object"].map(lambda x: get_survey_open_time(x.survey,tz_lookup,sdt))
    wsat=df["Object"].map(lambda x: localize_time(x.survey.updated,tz_lookup) if x.survey.answered else pd.NaT)

    df["Weekly Survey Was Opened"]=  wsot.map(lambda x: x is not pd.NaT) 
    df["Weekly Survey Was Answered"]=df["Object"].map(lambda x: x.survey.answered)

    df["Weekly Survey Opened Time"]=wsot
    df["Weekly Survey Answered Time"]=wsat
    #df['Weekly Survey Time Spent Answering'] = (wsat-wsot).map(lambda x: np.round(x.total_seconds(),1) if (x is not None and x is not np.nan and not pd.isnull(x)) else x)

    #Get survey answers dictionary and map
    df["answers"]=df["Object"].map(lambda x: x.survey.get_answers())
    answer_fields={'enjoy_activities_this_week':"Enjoyment of Activities",
        'lonely':"Loneliness",
        'important':"Intrinsic Motivation",
        'daily_routine':"Fit with Routine",
        'socially_connected':"Social Connectedness",
        'support':"Social Support",
        'other_people':"Extrinsic Motivation",
        'restless':"Negative Reinforcement",
    }
    for f,n in answer_fields.items():
        df[n]=df["answers"].map(lambda x: x[f] if f in x else None)

    #Set index and drop extra columns
    df["Particiant ID"]=username
    df = df.set_index(["Particiant ID", "Study Week"]) 
    df=df.drop(labels=["answers","Object"],axis=1)

    df.to_csv(os.path.join(directory,filename))
        
    print("  Wrote %d rows"%(len(df)))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))
    

def map_time_if_exists(df_field, tz):
    return df_field.astimezone(tz).replace(tzinfo=None) if df_field is not None else pd.NaT

#Localize a time
def localize_time(t,tz_lookup):
    if(t is None): return pd.NaT
    tz = tz_lookup[t.date()]
    local_t= t.astimezone(tz)
    return local_t

#Get localized time the survey page was opened
def get_survey_open_time(survey,tz_lookup,sdt):
    local_date = localize_time(survey.updated,tz_lookup).date()
    #print(local_date)
    if local_date in sdt:
        #print(local_date," in sdt")
        return sdt[local_date]["opened"]
    else:
        #print(local_date," not in sdt")
        return pd.NaT
