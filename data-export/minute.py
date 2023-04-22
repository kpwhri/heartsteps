import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone
from math import floor

from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate

def export_fitbit_minute_data(user, directory = None, filename = None, start=None, end=None, DEBUG=True):

    fitbit_account = user["fbid"]
    username = user["hsid"]

    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.minute_fitbit.csv'.format(
            username = username
        )
     
    #Get steps data
    query    = FitbitMinuteStepCount.objects.filter(account=fitbit_account).all().values('time','steps')
    df_steps = pd.DataFrame.from_records(query)
    df_steps = df_steps.rename(columns={"time":"Datetime"}, )
    df_steps = df_steps.set_index("Datetime")
    df_steps = df_steps.loc[~df_steps.index.duplicated()] #drop any duplicated index values

    #Get heart rate data
    query    = FitbitMinuteHeartRate.objects.filter(account=fitbit_account).all().values('time','heart_rate')
    df_hr    = pd.DataFrame.from_records(query)
    df_hr    = df_hr.rename(columns={"time":"Datetime"}, )
    df_hr    = df_hr.set_index("Datetime")
    df_hr    = df_hr.loc[~df_hr.index.duplicated()] #drop any duplicated index values

    #Get timezonedata
    query    = FitbitDay.objects.filter(account=fitbit_account).all().values('date','_timezone')
    df_tz    = pd.DataFrame.from_records(query)
    df_tz    = df_tz.rename(columns={"date":"Datetime", "_timezone":"timezone"}, )
    df_tz['Datetime'] = pd.to_datetime(df_tz['Datetime'], utc=True)
    df_tz    = df_tz.set_index("Datetime")

    import code
    code.interact(local=dict(globals(), **locals()))

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
    df["Participant ID"]=username
    df      = df.reset_index().set_index(["Participant ID", "datetime"])

    #Set missing steps to 0 when HR is defined
    df['steps'] = df['steps'].fillna(0) #Set all missing steps to 0
    df.loc[df['heart_rate'].isnull(), 'steps'] = np.nan #Reset to nan when hr is null

    #Export to csv
    df.to_csv(os.path.join(directory,filename))

    print("  Wrote %d rows"%(len(df)))
