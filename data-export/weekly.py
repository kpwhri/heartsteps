import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone
from logs import localize_time
from fitbit_activities.models import FitbitActivity
from weeks.models import Week
from surveys.models import Survey
from activity_plans.models import  ActivityPlan
from days.models import Day
from push_messages.models import Message
import logs

def export_weekly_planning(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    
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
    
    week_query = Week.objects.filter(user=uid).all()
    if not week_query:
        print("EMPTY QUERY: Week")
    df_week = pd.DataFrame.from_records(week_query.values('number','start_date','end_date','goal','confidence','survey_id'))
    df_week = df_week.set_index("number")
    df_week = df_week.drop(columns=['survey_id'])
    
    answers=[]
    barriers=[]
    planning=[]
    activities=[]
    
    for week in week_query:
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
    #utils.print_export_statistics(df_all_fields, 24)
    utils.verify_column_names(df_all_fields, os.path.join(directory,filename))

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
    if not week_query:
        print("EMPTY QUERY: Week")

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
    df=df.set_index("Study Week")

    #Re-map barriers list to string with : separator
    #There is not a fixed list of barriers
    df["Barriers"]=df["Barriers"].map(lambda x: ":".join(x) if x is not None else None)


    #Get survey indicators
    #Get days, timezones, and survey dwell time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAY QUERY")
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}
    sdt       = utils.estimate_survey_dwell_times(uid,survey_type="weekly")

    #Get notification indicators
    notification_query = Message.objects.filter(recipient=uid,title='Weekly reflection').order_by("created")
    if not notification_query:
        print("EMPTY QUERY: Message")
    df_msg = pd.DataFrame({'Object': [m for m in notification_query]})
    df_msg["Study Week"]    = df_msg["Object"].map(lambda x: x.data["currentWeek"]["id"])
    df_msg['Notification Was Sent']      = df_msg['Object'].map(lambda msg: "sent" in msg._message_receipts)
    df_msg['Notification Was Received']  = df_msg['Object'].map(lambda msg: "received" in msg._message_receipts)
    df_msg['Notification Was Opened']    = df_msg['Object'].map(lambda msg: "opened" in msg._message_receipts)
    df_msg['Notification Time Sent']     = df_msg['Object'].map(lambda msg: localize_time(msg._message_receipts["sent"], tz_lookup) if "sent" in msg._message_receipts else pd.NaT)
    df_msg['Notification Time Received'] = df_msg['Object'].map(lambda msg: localize_time(msg._message_receipts["received"], tz_lookup) if "received" in msg._message_receipts else pd.NaT)
    df_msg['Notification Time Opened']   = df_msg['Object'].map(lambda msg: localize_time(msg._message_receipts["opened"], tz_lookup) if "opened" in msg._message_receipts else pd.NaT)
    df_msg=df_msg.drop(labels="Object", axis=1)
    df_msg = df_msg.set_index("Study Week")

    #Join weekly survey with notifications
    df = df.join(df_msg, how="outer")

    #Get survey open and answer times
    wsot=df["Object"].map(lambda x: get_survey_open_time(x.survey,tz_lookup,sdt))
    wsat=df["Object"].map(lambda x: localize_time(x.survey.updated,tz_lookup) if x.survey.answered else pd.NaT)

    #Create fields
    df["Survey Was Opened"]=wsot.map(lambda x: x is not pd.NaT)
    df["Survey Was Answered"]=df["Object"].map(lambda x: x.survey.answered)

    df["Survey Time Opened"]=wsot
    df["Survey Time Answered"]=wsat

    # wsat.dtype = Object and wsot.dtype = datetime64[ns, timezone] typeError for subtraction
    time_spent = pd.to_datetime(wsat, utc=True) - pd.to_datetime(wsot, utc=True)

    df['Survey Time Spent Answering'] = time_spent.map(lambda x: np.round(x.total_seconds(),1) if (x is not None and x is not np.nan and not pd.isnull(x)) else x)

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

    #Mam time fields to strings
    time_fields = ['Notification Time Sent',
                   'Notification Time Received',
                   'Notification Time Opened',
                   "Survey Time Opened",
                   "Survey Time Answered"]
    for f in time_fields:
        df[f] = df[f].map(to_time_str)

    df = df.reset_index()
    df = df.set_index(["Particiant ID", "Study Week"]) 
    df = df.drop(labels=["answers","Object"],axis=1)

    #utils.print_export_statistics(df, 25)

    utils.verify_column_names(df, os.path.join(directory, filename))
    df.to_csv(os.path.join(directory,filename))
        
    print("  Wrote %d rows"%(len(df)))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

def export_weekly_fitbit_activity_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    pass
def export_weekly_app_use_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    uid = user["uid"]
    username = user["hsid"]

    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.weekly_app_use.csv'.format(username=username)

    if ((not from_scratch) and os.path.isfile(os.path.join(directory, filename))):
        return

    # Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date', 'end_date', 'number')
    if not week_query:
        print("EMPTY QUERY: Week")

    df_weeks = pd.DataFrame.from_records(week_query)

    # Get base data from fitbit activity log
    df = logs.export_app_use_log(user, directory=directory, filename=filename, from_scratch=from_scratch, DEBUG=DEBUG,
                                 save=False)
    df["Date"] = df["Datetime"].map(lambda x: pd.to_datetime(x).date())
    df["Total App Views"] = 1

    df["Study Week"] = df["Date"].map(lambda day: df_weeks[(day >= df_weeks['start_date']) & (day <= df_weeks['end_date'])]['number'].values[0])

    df1 = df[["Study Week", "Total App Views"]].groupby("Study Week").sum()

    df_join = df1.join(df_weeks, how="outer")
    df_join = df_join.reset_index()

    df_join["Participant ID"] = username
    df_join = df_join.set_index(["Participant ID", "start_date"])
    df_join = df_join.fillna(0)

    #utils.verify_column_names(df_join, os.path.join(directory, filename))
    df_join.to_csv(os.path.join(directory, filename))

    if (DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

def export_weekly_notification_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    uid = user["uid"]
    username = user["hsid"]

    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.weekly_notifications.csv'.format(username=username)

    if ((not from_scratch) and os.path.isfile(os.path.join(directory, filename))):
        return

    # Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date', 'end_date', 'number')
    if not week_query:
        print("EMPTY QUERY: Week")

    df_weeks = pd.DataFrame.from_records(week_query)

    # Get base data from notifications log
    df = logs.export_notification_log(user, directory=directory, filename=filename, from_scratch=from_scratch,
                                      DEBUG=DEBUG, save=False)

    df["Date"] = df["Datetime"].map(lambda x: pd.to_datetime(x).date())

    df["Study Week"] = df["Date"].map(lambda day: df_weeks[(day >= df_weeks['start_date']) & (day <= df_weeks['end_date'])]['number'].values[0])

    df1 = df[["Study Week", 'Notification Was Sent', 'Notification Was Received', 'Notification Was Opened']].groupby(
        "Study Week").sum()

    column_map = {'Notification Was Sent': "Total Notifications Sent",
                  'Notification Was Received': "Total Notifications Received",
                  'Notification Was Opened': "Total Notifications Opened",
                  }
    df1 = df1.rename(columns=column_map)

    df_join = df1.join(df_weeks, how="outer")
    df_join = df_join.reset_index()

    df_join["Participant ID"] = username
    df_join = df_join.set_index(["Participant ID", "start_date"])
    df_join = df_join.fillna(0)

    utils.verify_column_names(df_join, os.path.join(directory, filename))
    df_join.to_csv(os.path.join(directory, filename))

    if (DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))
def export_weekly_morning_message(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    pass
def export_weekly_walking_suggestions(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    pass

def export_weekly_antidesentary_suggestions(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    pass
def export_weekly_fitbit_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    pass

def map_time_if_exists(df_field, tz):
    return df_field.astimezone(tz).replace(tzinfo=None) if df_field is not None else pd.NaT

#Get localized time the survey page was opened
def get_survey_open_time(survey,tz_lookup,sdt):
    local_date = localize_time(survey.updated,tz_lookup).date()
    #print(local_date)
    if local_date in sdt:
        #print(local_date," in sdt")
        return localize_time(sdt[local_date]["opened"],tz_lookup)
    else:
        #print(local_date," not in sdt")
        return pd.NaT

def to_time_str(x):
    if( x is not np.nan and x is not None and not pd.isnull(x)):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return x