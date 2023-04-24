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
from push_messages.models import Message

def export_fitbit_activity_log(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

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
    df = pd.DataFrame({'Object': [x for x in queryset]})

    #Get basic fields
    fields = {'start_time':"Datetime", 'end_time':"End Time", 'average_heart_rate':'Average Heart Rate'}
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
    for f,n in fields.items():
        df[n] = df["Object"].map(lambda x: x.payload[f] if f in x.payload else np.nan)

    #Set index and drop extra columns
    df["Particiant ID"]=username

    #Get survey indicators
    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}

    #Map time fields to strings
    time_fields = ["Datetime",
                   "End Time"]
    for f in time_fields:
        df[f] = df[f].map(lambda x:localize_time(x,tz_lookup))
        df[f] = df[f].map(to_time_str)

    df = df.set_index(["Particiant ID"]) 
    df = df.drop(labels=["Object"],axis=1)

    df.to_csv(os.path.join(directory, filename))


    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

#Localize a time
def localize_time(t,tz_lookup):
    if(t is None): return pd.NaT
    tz = tz_lookup[t.date()]
    local_t= t.astimezone(tz)
    return local_t

def to_time_str(x):
    if( x is not np.nan and x is not None and not pd.isnull(x)):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return x