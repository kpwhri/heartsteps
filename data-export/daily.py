import pandas as pd
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone
from math import floor

import utils, logs, within_day, minute

from days.models import Day
from push_messages.models import Message as PushMessage
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from weeks.models import Week
from activity_plans.models import  ActivityPlan
from morning_messages.models import MorningMessage

def export_daily_planning_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
        
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_planning.csv'.format(
            username = username
        )
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates = df_dates.set_index(["Date"])

    #Get base data from planning log
    df = logs.export_planning_log(user,directory = directory, filename = filename, from_scratch=from_scratch,DEBUG=DEBUG,save=False)
    df["Date"]=df["Datetime"].map(lambda x: pd.to_datetime(x).date())
    df["Activity Date"] = df["Activity Datetime"].map(lambda x: pd.to_datetime(x).date())
    df["Duration Marked Completed"]=df["Duration"]*df["Marked Completed"]
    df["Number"]=1

    #Group activities by date they were created
    df1 = df[["Date","Duration","Duration Marked Completed","Vigorous","Number","Marked Completed"]].groupby("Date").sum()
    column_map1={"Number":"Number of Activities Planned on This Day",
                        "Vigorous":"Number of Activities Planned on This Day Marked Vigorous",
                        "Marked Completed":"Number of Activities Planned on This Day Marked Completed",
                        "Duration":"Total Duration of Activities Planned on This Day",
                        "Duration Marked Completed":"Total Duration of Activities Planned on This Day Marked Completed"
                }
    df1 = df1.rename(columns=column_map1)

    #Group activities by date they were planned to be performed on
    df2 = df[["Activity Date","Duration","Duration Marked Completed","Vigorous","Number","Marked Completed"]].groupby("Activity Date").sum()
    column_map2={"Number":"Number of Activities Planned for This Day",
                        "Vigorous":"Number of of Activities Planned for This Day Marked Vigorous",
                        "Marked Completed":"Number of Activities Planned for This Day Marked Completed",
                        "Duration":"Total Duration of Activities Planned for This Day",
                        "Duration Marked Completed":"Total Duration of Activities Planned for This Day Marked Completed"
                }
    df2 = df2.rename(columns=column_map2)
    df2.index = df2.index.rename("Date")

    if not df["Duration"].empty:
        df1 = df1[list(column_map1.values())]
        df2 = df2[list(column_map2.values())]
    else:
        df1[list(column_map1.values())] = np.nan
        df2[list(column_map2.values())] = np.nan

    df_join = df1.join(df2,how="outer").join(df_dates,how="outer")
    df_join = df_join.fillna(0)
    df_join = df_join.reset_index()

    df_join["Participant ID"]=username
    df_join = df_join.set_index(["Participant ID","Date"])
    utils.print_export_statistics(df_join, 10)
    df_join.to_csv(os.path.join(directory,filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

def export_daily_fitbit_activity_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
        
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_fitbit_activity.csv'.format(username = username)
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates = df_dates.set_index(["Date"])

    #Get base data from fitbit activity log
    df = logs.export_fitbit_activity_log(user,directory = directory, filename = filename, from_scratch=from_scratch,DEBUG=DEBUG,save=False)
    df["Date"]=df["Datetime"].map(lambda x: pd.to_datetime(x).date())
    df["Number of Activity Bouts"]=1

    df1 = df.groupby("Date").sum()
    df2 = df.groupby("Date").mean()

    df1["Average Heart Rate"] = key_does_not_exist_handler(uid, "Average Heart Rate", df2)
    df1["Has Active Zone Minutes"] = key_does_not_exist_handler(uid, "Has Active Zone Minutes", df1)>0

    df_join = df1.join(df_dates,how="outer")
    df_join = df_join.reset_index()

    df_join["Participant ID"]=username
    df_join = df_join.set_index(["Participant ID","Date"])

    utils.print_export_statistics(df_join, 7)
    df_join.to_csv(os.path.join(directory,filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

def export_daily_app_use_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
        
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_app_use.csv'.format(username = username)
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates = df_dates.set_index(["Date"])

    #Get base data from fitbit activity log
    df = logs.export_app_use_log(user,directory = directory, filename = filename, from_scratch=from_scratch,DEBUG=DEBUG,save=False)
    df["Date"]=df["Datetime"].map(lambda x: pd.to_datetime(x).date())
    df["Total App Views"]=1

    df1 = df[["Date","Total App Views"]].groupby("Date").sum()

    df_join = df1.join(df_dates,how="outer")
    df_join = df_join.reset_index()

    df_join["Participant ID"]=username
    df_join = df_join.set_index(["Participant ID","Date"])
    df_join=df_join.fillna(0)

    utils.print_export_statistics(df_join, 1)
    df_join.to_csv(os.path.join(directory,filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

def export_daily_notification_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
        
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_notifications.csv'.format(username = username)
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates = df_dates.set_index(["Date"])

    #Get base data from fitbit activity log
    df = logs.export_notification_log(user,directory = directory, filename = filename, from_scratch=from_scratch,DEBUG=DEBUG,save=False)
    df["Date"]=df["Datetime"].map(lambda x: pd.to_datetime(x).date())

    df1 = df[["Date",'Notification Was Sent','Notification Was Received','Notification Was Opened']].groupby("Date").sum()

    column_map={'Notification Was Sent':"Total Notifications Sent",
                'Notification Was Received':"Total Notifications Received",
                'Notification Was Opened':"Total Notifications Opened",
                }
    df1 = df1.rename(columns=column_map)

    df_join = df1.join(df_dates,how="outer")
    df_join = df_join.reset_index()

    df_join["Participant ID"]=username
    df_join = df_join.set_index(["Participant ID","Date"])
    df_join=df_join.fillna(0)

    utils.print_export_statistics(df_join, 3)
    df_join.to_csv(os.path.join(directory,filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

def export_daily_walking_suggestions(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
        
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_walking_suggestions.csv'.format(username = username)
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates = df_dates.set_index(["Date"])

    #Get base data from fitbit activity log
    df = within_day.walking_suggestions(user,directory = directory, filename = filename, from_scratch=from_scratch,DEBUG=DEBUG,save=False)
    df=df.reset_index()
    df["Date"]=df["Datetime"].map(lambda x: pd.to_datetime(x).date())

    df1 = df[["Date",'Notification Was Sent','Notification Was Received','Notification Was Opened']].groupby("Date").sum()

    column_map={'Notification Was Sent':"Total Notifications Sent",
                'Notification Was Received':"Total Notifications Received",
                'Notification Was Opened':"Total Notifications Opened",
                }
    df1 = df1.rename(columns=column_map)

    df_join = df1.join(df_dates,how="outer")
    df_join = df_join.reset_index()

    df_join["Participant ID"]=username
    df_join = df_join.set_index(["Participant ID","Date"])
    df_join=df_join.fillna(0)

    utils.print_export_statistics(df_join, 3)
    df_join.to_csv(os.path.join(directory,filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))


def export_daily_antidesentary_suggestions(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
        
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_antidesentary_suggestions.csv'.format(username = username)
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates = df_dates.set_index(["Date"])

    #Get base data from fitbit activity log
    df = within_day.antisedentary_suggestions(user, directory=directory, filename=filename, from_scratch=from_scratch,
                                              DEBUG=DEBUG, save=False)
    df=df.reset_index()
    df["Date"]=df["Datetime"].map(lambda x: pd.to_datetime(x).date())

    df1 = df[["Date",'Notification Was Sent','Notification Was Received','Notification Was Opened']].groupby("Date").sum()

    column_map={'Notification Was Sent':"Total Notifications Sent",
                'Notification Was Received':"Total Notifications Received",
                'Notification Was Opened':"Total Notifications Opened",
                }
    df1 = df1.rename(columns=column_map)

    df_join = df1.join(df_dates,how="outer")
    df_join = df_join.reset_index()

    df_join["Participant ID"]=username
    df_join = df_join.set_index(["Participant ID","Date"])
    df_join=df_join.fillna(0)

    utils.print_export_statistics(df_join, 3)
    df_join.to_csv(os.path.join(directory,filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

def export_daily_fitbit_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
        
    uid = user["uid"]
    username = user["hsid"]
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_fitbit.csv'.format(username = username)
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates = df_dates.set_index(["Date"])

    #Get base data from fitbit activity log
    df = minute.export_fitbit_minute_data(user,directory = directory, filename = filename, from_scratch=from_scratch,DEBUG=DEBUG,save=False)
    df=df.reset_index()
    df["Date"]=df["Datetime"].map(lambda x: pd.to_datetime(x).date())
    df["Valid Hours"]=1/60

    df1 = df[["Date",'Steps',"Valid Hours"]].groupby("Date").sum()
    df2 = df[["Date",'Heart Rate']].groupby("Date").mean()

    df_join = df1.join(df_dates,how="outer").join(df2,how="outer")
    df_join = df_join.reset_index()

    df_join = df_join[['Date','Steps','Heart Rate',"Valid Hours"]]

    df_join["Participant ID"]=username
    df_join = df_join.set_index(["Participant ID","Date"])
    df_join=df_join.fillna(0)

    utils.print_export_statistics(df_join, 3)
    df_join.to_csv(os.path.join(directory,filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))


def export_daily_morning_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from MorningMessage data model and export to csv
    Reference task: export_morning_message_survey in server/morning_messages/tasks.py
    """

    uid = user["uid"]
    username = user["hsid"]

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_morning_survey.csv'.format(
            username=username
        )

    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    # Get all weeks where participant may have received survey
    week_query = Week.objects.filter(user=uid).all().values('start_date', 'end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days + 1)]

    days = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAY QUERY")
    day_lookup = {x.date: x.timezone for x in days}
    tzs = [day_lookup[date] if date in day_lookup else np.nan for date in dates ] 

    # Create a dataframe with each day in range and hsid
    df_dates = pd.DataFrame({"Date": dates})
    df_dates["Participant ID"] = username

    # Model Structure: MorningMessage -> MorningMessageSurvey -> Survey -> Q/A
    # Query all MorningMessages for user
    morning_messages = MorningMessage.objects \
        .order_by('date') \
        .filter(
            user=uid
        ) \
        .prefetch_decision() \
        .prefetch_message() \
        .prefetch_survey() \
        .prefetch_timezone() \
        .all()

    if not morning_messages:
        print("EMPTY QUERY: MorningMessage")
    # MorningMessage question names for consistent headers across all users
    questions_headers = ['busy', 'rested', 'committed', 'mm_extrinsic_motivation', 'extrinsic', 'mm_intrinsic_motivation', 'intrinsic']

    # Construct DataFrame
    if morning_messages:

        # Map each time attribute if exists, otherwise np.nan
        df_morning_messages = pd.DataFrame({'Object': [msg for msg in morning_messages]})
        df_morning_messages['Date'] = df_morning_messages['Object'].map(lambda msg: msg.date)

        #Try mapping survey open and close times
        sdt = utils.estimate_survey_dwell_times(uid,survey_type="morning")
        survey_open_map = lambda msg: map_time_if_exists(sdt[msg.date]["opened"],msg.timezone) if msg.date in sdt else pd.NaT
        #survey_close_map = lambda msg: map_time_if_exists(sdt[msg.date]["closed"] ,msg.timezone) if msg.date in sdt else np.nan

        msot = df_morning_messages['Object'].map(survey_open_map)
        msat = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.survey.answered_at, msg.timezone) if (msg.survey is not None and msg.survey.answered) else pd.NaT)

        df_morning_messages['Morning Survey Was Opened'] = msot.apply(lambda x: x is not np.nan and x is not None and not pd.isnull(x))
        df_morning_messages['Morning Survey Was Answered'] = msat.apply(lambda x: x is not np.nan and x is not None and not pd.isnull(x))

        #import code
        #code.interact(local=dict(globals(), **locals()))

        df_morning_messages['Morning Survey Opened Time'] = msot.apply(to_time)
        df_morning_messages['Morning Survey Answered Time'] = msat.apply(to_time)
        df_morning_messages['Morning Survey Time Spent Answering'] = (msat-msot).map(lambda x: np.round(x.total_seconds(),1) if (x is not None and x is not np.nan and not pd.isnull(x)) else x)
        
        #import code
        #code.interact(local=dict(globals(), **locals()))

        # Map each question to response title if answered
        for question in questions_headers:
            df_morning_messages[question.title()] = df_morning_messages['Object'].map(lambda msg: map_dict_if_key_exists(msg.survey.get_answers(), question) if msg.survey is not None else np.nan)

        # Merge intrinsic/extrinsic columns (old and new question)
        df_morning_messages['extrinsic'.title()] = df_morning_messages['extrinsic'.title()].combine_first(df_morning_messages['mm_extrinsic_motivation'.title()])
        df_morning_messages['intrinsic'.title()] = df_morning_messages['intrinsic'.title()].combine_first(df_morning_messages['mm_intrinsic_motivation'.title()])

        # Collect mood from answers dictionary
        df_morning_messages['Mood'] = df_morning_messages['Object'].map(lambda msg: map_dict_if_key_exists(msg.survey.get_answers(), 'selected_word') if msg.survey is not None else np.nan)

        # Drop 'Object' column
        df_morning_messages.drop('Object', axis=1, inplace=True)

        #Keep last morning message entry for each date if there are spurious duplicates
        df_morning_messages = utils.deduplicate_dates(df_morning_messages,"Date")

        # Outer join df_dates to include participant duration of study
        result = df_dates.join(df_morning_messages.set_index('Date'), on="Date", how="outer")
    
    else:
        print('  EMPTY QUERY -- no data found')

        df_dates[["Morning Survey Was Opened","Morning Survey Was Answered","Morning Survey Opened Time","Morning Survey Answered Time","Morning Survey Time Spent Answering"]] = np.nan

        df_dates[[question.title() for question in questions_headers]] = np.nan

        df_dates['Mood'] = np.nan
        result = df_dates

    result=result.fillna({'Morning Survey Was Opened':False,'Morning Survey Was Answered':False})

    # Drop extra intrinsic/extrinsic columns
    result.drop('mm_extrinsic_motivation'.title(), axis=1, inplace=True)
    result.drop('mm_intrinsic_motivation'.title(), axis=1, inplace=True)

    # Set Date as index of DataFrame
    utils.print_export_statistics(result, 13)
    result.set_index(["Participant ID",'Date']).to_csv(os.path.join(directory, filename))

    print("  Wrote %d rows" % (len(result)))


def export_daily_morning_message(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from MorningMessage data model and export to csv
    Reference task: export_morning_message_survey in server/morning_messages/tasks.py
    """

    uid = user["uid"]
    username = user["hsid"]

    if DEBUG:
        print("  Exporting daily morning message data for: ", username)

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_morning_message.csv'.format(
            username=username
        )

    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    # Get all weeks where participant may have received survey
    week_query = Week.objects.filter(user=uid).all().values('start_date', 'end_date')
    if not week_query:
        print("EMPTY QUERY: Week")
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days + 1)]

    days = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAY QUERY")
    day_lookup = {x.date: x.timezone for x in days}
    tzs = [day_lookup[date] if date in day_lookup else np.nan for date in dates ] 

    # Create a dataframe with each day in range and hsid
    df_dates = pd.DataFrame({"Date": dates})
    df_dates["Participant ID"] = username

    # Model Structure: MorningMessage -> MorningMessageSurvey -> Survey -> Q/A
    # Query all MorningMessages for user
    morning_messages = MorningMessage.objects \
        .order_by('date') \
        .filter(
            user=uid
        ) \
        .prefetch_decision() \
        .prefetch_message() \
        .prefetch_timezone() \
        .all()

    if not morning_messages:
        print("EMPTY QUERY: MorningMessage")

    # Construct DataFrame
    if morning_messages:

        # Map each time attribute if exists, otherwise np.nan
        df_morning_messages = pd.DataFrame({'Object': [msg for msg in morning_messages]})
        df_morning_messages['Date']            = df_morning_messages['Object'].map(lambda msg: msg.date)
        df_morning_messages['Was Sent']        = df_morning_messages['Object'].map(lambda msg: bool(msg.message.sent) if msg.message is not None else 'False')
        df_morning_messages['Was Received']    = df_morning_messages['Object'].map(lambda msg: bool(msg.message.received) if msg.message is not None else 'False')
        df_morning_messages['Was Opened']      = df_morning_messages['Object'].map(lambda msg: bool(msg.message.opened) if msg.message is not None else 'False')
        df_morning_messages['Time Sent']       = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.message.sent, msg.timezone) if msg.message is not None else np.nan)
        df_morning_messages['Time Received']   = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.message.received, msg.timezone) if msg.message is not None else np.nan)
        df_morning_messages['Time Opened']     = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.message.opened, msg.timezone) if msg.message is not None else np.nan)
        df_morning_messages['Randomized']      = df_morning_messages['Object'].map(lambda msg: msg.randomized)
        df_morning_messages['Notification']    = df_morning_messages['Object'].map(lambda msg: msg.notification)
        df_morning_messages['Text']            = df_morning_messages['Object'].map(lambda msg: msg.text)
        df_morning_messages['Anchor']          = df_morning_messages['Object'].map(lambda msg: msg.anchor)
        df_morning_messages['Gain Frame']      = df_morning_messages['Object'].map(lambda msg: msg.is_gain_framed)
        df_morning_messages['Loss Frame']      = df_morning_messages['Object'].map(lambda msg: msg.is_loss_framed)
        df_morning_messages['Activity Frame']  = df_morning_messages['Object'].map(lambda msg: msg.is_active_framed)
        df_morning_messages['Sedentary Frame'] = df_morning_messages['Object'].map(lambda msg: msg.is_sedentary_framed)

        #import code
        #code.interact(local=dict(globals(), **locals()))

        # Drop 'Object' column
        df_morning_messages.drop('Object', axis=1, inplace=True)

        #Keep last morning message entry for each date if there are spurious duplicates
        df_morning_messages = utils.deduplicate_dates(df_morning_messages,"Date")

        # Outer join df_dates to include participant duration of study
        result = df_dates.join(df_morning_messages.set_index('Date'), on="Date", how="outer")
    
    else:
        print('  EMPTY QUERY -- no data found')

        df_dates[['Date', 'Was Sent', 'Was Received', 'Was Opened', 'Time Sent', 'Time Received', 'Time Opened', 'Randomized', 'Notification', 'Text', 'Anchor', 'Gain Frame', 'Loss Frame', 'Activity Frame', 'Sedentary Frame']] = np.nan

        result = df_dates

    result=result.fillna({'Was Sent':False,'Was Received':False,'Was Opened':False})

    # Set Date as index of DataFrame
    utils.print_export_statistics(result, 16)
    result.set_index(["Participant ID",'Date']).to_csv(os.path.join(directory, filename))

    
    print("  Wrote %d rows" % (len(result)))


def key_does_not_exist_handler(uid, datafield, df):
    try:
        return df[datafield]
    except KeyError:
        #print(f"User UID: ({uid}) EMPTY {datafield}")
        return np.nan

def map_time_if_exists(df_field, tz):
    return df_field.astimezone(tz).replace(tzinfo=None) if df_field is not None else pd.NaT

def to_time(x):
    if( x is not np.nan and x is not None and not pd.isnull(x)):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return x

def map_dict_if_key_exists(d, key):
    return d[key] if d is not None and key in d.keys() and d[key] is not None else np.nan