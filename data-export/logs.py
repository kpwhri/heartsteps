import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone

from fitbit_activities.models import FitbitActivity
from days.models import Day
from push_messages.models import Message
from page_views.models import PageView
from activity_plans.models import  ActivityPlan

def export_fitbit_activity_log(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True,save=True):

    fitbit_account = user["fbid"]
    username = user["hsid"]
    uid = user["uid"]

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.logs.fitbit_activities.csv'.format(
            username=username
        )
    
    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    #Only use fitbit activities                            
    queryset = FitbitActivity.objects.filter(account_id=user["fbid"]).order_by('start_time').all()
    if not queryset:
        print("EMPTY QUERY: FitbitActivity")
        df = utils.create_empty_export(os.path.join(directory, filename))
        if (save):
            utils.verify_column_names(df, os.path.join(directory, filename))
            df.to_csv(os.path.join(directory, filename))

    df = pd.DataFrame({'Object': [x for x in queryset]})

    #Get basic fields
    fields = {'start_time':"Datetime", 'end_time':"End Time", 'average_heart_rate':'Average Heart Rate'}
    df[list(fields.values())] = np.nan
    for f,n in fields.items():
        df[n] = df["Object"].map(lambda x: getattr(x,f))

    df["Duration"] = (df["End Time"]-df["Datetime"])
    df["Duration"] = df["Duration"].map(lambda x: np.round(x.total_seconds() / 60,1)) 

    #Get basic fitbit log fields
    fields={'activityName':'Activity Name',
            'logType':"Log Type", 
            "steps":"Steps",
            "calories":'Calories',
            'elevationGain':'Elevation Gain',
            'hasActiveZoneMinutes':'Has Active Zone Minutes'}
    df[list(fields.values())] = np.nan
    for f,n in fields.items():
        df[n] = df["Object"].map(lambda x: x.payload[f] if x.payload and f in x.payload else np.nan)

    #Set index and drop extra columns
    df["Particiant ID"]=username

    #Get survey indicators
    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAYS QUERY")
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}

    #Map time fields to strings
    time_fields = ["Datetime",
                   "End Time"]
    for f in time_fields:
        df[f] = df[f].map(lambda x:localize_time(x,tz_lookup))
        df[f] = df[f].map(to_time_str)

    df = df.set_index(["Particiant ID"]) 
    df = df.drop(labels=["Object"],axis=1)

    if(save):
        #utils.print_export_statistics(df, 10)
        utils.verify_column_names(df, os.path.join(directory, filename))
        df.to_csv(os.path.join(directory, filename))

    if(DEBUG and save):
        import code
        code.interact(local=dict(globals(), **locals()))

    return df

def export_notification_log(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True,save=True):

    fitbit_account = user["fbid"]
    username = user["hsid"]
    uid = user["uid"]

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.logs.notification.csv'.format(
            username=username
        )
    
    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    #Get notification indicators
    notification_query = Message.objects.filter(recipient=uid).order_by("created")
    if not notification_query:
        print("EMPTY QUERY: Message")
        df = utils.create_empty_export(os.path.join(directory, filename))
        if (save):
            utils.verify_column_names(df, os.path.join(directory, filename))
            df.to_csv(os.path.join(directory, filename))

    df = pd.DataFrame({'Object': [m for m in notification_query]})
    df['Datetime']                   = df['Object'].map(lambda msg: msg.created)
    df['Notification Title']          = df['Object'].map(lambda msg: msg.title)
    df['Notification Was Sent']      = df['Object'].map(lambda msg: "sent" in msg._message_receipts)
    df['Notification Was Received']  = df['Object'].map(lambda msg: "received" in msg._message_receipts)
    df['Notification Was Opened']    = df['Object'].map(lambda msg: "opened" in msg._message_receipts)
    df['Notification Time Sent']     = df['Object'].map(lambda msg: msg._message_receipts["sent"]  if "sent" in msg._message_receipts else pd.NaT)
    df['Notification Time Received'] = df['Object'].map(lambda msg: msg._message_receipts["received"] if "received" in msg._message_receipts else pd.NaT)
    df['Notification Time Opened']   = df['Object'].map(lambda msg: msg._message_receipts["opened"] if "opened" in msg._message_receipts else pd.NaT)

    #Get survey indicators
    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAY QUERY")
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}

    #Map time fields to strings
    time_fields = ['Datetime',
                   'Notification Time Sent',
                   'Notification Time Received',
                   'Notification Time Opened']
    for f in time_fields:
        df[f] = df[f].map(lambda x:localize_time(x,tz_lookup))
        df[f] = df[f].map(to_time_str)

    #Set index and drop extra columns
    df["Particiant ID"]=username
    df = df.set_index(["Particiant ID"]) 
    df = df.drop(labels=["Object"],axis=1)

    if(save):
        #utils.print_export_statistics(df, 8)
        utils.verify_column_names(df, os.path.join(directory, filename))
        df.to_csv(os.path.join(directory, filename))

    if(DEBUG and save):
        import code
        code.interact(local=dict(globals(), **locals()))

    return df

def export_app_use_log(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True,save=True):

    fitbit_account = user["fbid"]
    username = user["hsid"]
    uid = user["uid"]

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.logs.app_use.csv'.format(
            username=username
        )
    
    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    queryset=PageView.objects.filter(user_id=uid).order_by("created").all()
    if not queryset:
        print("EMPTY QUERY: PageView")
        df = utils.create_empty_export(os.path.join(directory, filename))
        if (save):
            utils.verify_column_names(df, os.path.join(directory, filename))
            df.to_csv(os.path.join(directory, filename))
    df = pd.DataFrame({'Object': [m for m in queryset]})
    df['Datetime']        = df['Object'].map(lambda msg: msg.created)

    df['App URI']         = df['Object'].map(lambda msg: msg.uri)
    df['App URI']         = df['App URI'].map(lambda x: "/notification/*." if "/notification/" in x else x) 
    df['App URI']         = df['App URI'].map(lambda x: "/plans/*" if "/plans/" in x else x) 
    df['App URI']         = df['App URI'].map(lambda x: "/activities/logs/*" if "/activities/logs/" in x else x)

    #Get survey indicators
    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAY QUERY")
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}

    #Map time fields to strings
    time_fields = ['Datetime']
    for f in time_fields:
        df[f] = df[f].map(lambda x:localize_time(x,tz_lookup))
        df[f] = df[f].map(to_time_str)

    #Set index and drop extra columns
    df["Particiant ID"]=username
    df = df.set_index(["Particiant ID"]) 
    df = df.drop(labels=["Object"],axis=1)

    if(save):
        #utils.print_export_statistics(df, 2)
        utils.verify_column_names(df, os.path.join(directory, filename))
        df.to_csv(os.path.join(directory, filename))

    if(DEBUG and save):
        import code
        code.interact(local=dict(globals(), **locals()))

    return df

def export_planning_log(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True, save=True):

    username = user["hsid"]
    uid = user["uid"]

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.logs.planning.csv'.format(
            username=username
        )
    
    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    queryset = ActivityPlan.objects.filter(user_id=uid).order_by("created_at").all()
    if not queryset:
        print("EMPTY QUERY: ActivityPlan")
        df = utils.create_empty_export(os.path.join(directory, filename))
        if (save):
            utils.verify_column_names(df, os.path.join(directory, filename))
            df.to_csv(os.path.join(directory, filename))
    df = pd.DataFrame({'Object': [m for m in queryset]})

    fields={"created_at":"Datetime",
            "start":"Activity Datetime",
            'timeOfDay':"Time of Day",
            'duration':"Duration",
            'vigorous':"Vigorous",
            'type_id':"Type"}
    for f,n in fields.items():
        df[n] = df["Object"].map(lambda x: getattr(x,f))

    df["Marked Completed"] = df["Object"].map(lambda x: x.activity_log_id is not None)

    #Get survey indicators
    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAY QUERY")
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}

    #Map time fields to strings
    time_fields = ['Datetime',"Activity Datetime"]
    for f in time_fields:
        df[f] = df[f].map(lambda x:localize_time(x,tz_lookup))
        df[f] = df[f].map(to_time_str)

    #Set index and drop extra columns
    df["Particiant ID"]=username
    df = df.set_index(["Particiant ID"]) 
    df = df.drop(labels=["Object"],axis=1)

    if(save):
        #utils.print_export_statistics(df, 7)
        utils.verify_column_names(df, os.path.join(directory, filename))
        df.to_csv(os.path.join(directory, filename))

    if(DEBUG and save):
        import code
        code.interact(local=dict(globals(), **locals()))

    return df

#Localize a time
def localize_time(t,tz_lookup):
    if(tz_lookup is None or t is None or t is pd.NaT or pd.isnull(t)): return pd.NaT
    try:
        tz = tz_lookup[t.date()]
        local_t = t.astimezone(tz)
    except KeyError:
        print(f'ERROR: key {t}, but tz_lookup range {list(tz_lookup.keys())[0]}-{list(tz_lookup.keys())[-1]}')
        print('Trying to find closest date...')
        #np.fromiter(tz_lookup.keys(), dtype)
        logged_dates = np.array(list(tz_lookup.keys()))
        tz = tz_lookup[logged_dates[np.argmin(np.abs(logged_dates - t.date()))]]
        local_t = t.astimezone(tz)
    return local_t

def to_time_str(x):
    if( x is not np.nan and x is not None and not pd.isnull(x)):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return x