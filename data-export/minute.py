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

def strip_time_if_exists(x):
    return x.replace(tzinfo=None) if x is not None else pd.NaT

def to_time(x):
    if( x is not np.nan and x is not None and not pd.isnull(x)):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return x

def export_fitbit_minute_data(user, directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True,save=True):

    fitbit_account = user["fbid"]
    username = user["hsid"]

    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.minute_fitbit.csv'.format(
            username = username
        )
    
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
     
    #Get steps data
    query    = FitbitMinuteStepCount.objects.filter(account=fitbit_account).all().values('time','steps')
    if not query:
        print("EMPTY QUERY: FitbitMinuteStepCount")
    df_steps = pd.DataFrame.from_records(query)
    df_steps = df_steps.rename(columns={"time":"Datetime",'steps':"Steps"})
    df_steps["Datetime"]=df_steps["Datetime"].apply(strip_time_if_exists)
    df_steps = df_steps.set_index("Datetime")
    df_steps = df_steps.loc[~df_steps.index.duplicated()] #drop any duplicated index values

    #Get heart rate data
    query    = FitbitMinuteHeartRate.objects.filter(account=fitbit_account).all().values('time','heart_rate')
    if not query:
        print("EMPTY QUERY: FitbitMinuteHeartRate")
    df_hr    = pd.DataFrame.from_records(query)
    df_hr    = df_hr.rename(columns={"time":"Datetime",'heart_rate':"Heart Rate"}, )
    df_hr["Datetime"]=df_hr["Datetime"].apply(strip_time_if_exists)
    df_hr    = df_hr.set_index("Datetime")
    df_hr    = df_hr.loc[~df_hr.index.duplicated()] #drop any duplicated index values

    #Get timezonedata
    #Is fitbit data in participant local time already?
    query    = FitbitDay.objects.filter(account=fitbit_account).all().values('date','_timezone')
    if not query:
        print("EMPTY QUERY: FitbitDay")
    df_tz    = pd.DataFrame.from_records(query)
    df_tz    = df_tz.rename(columns={"date":"Datetime", "_timezone":"timezone"}, )
    df_tz['Datetime'] = pd.to_datetime(df_tz['Datetime'], utc=True)
    df_tz    = df_tz.set_index("Datetime")

    '''
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
    '''
    #Join all datafames and set index
    df      = pd.concat([df_steps,df_hr],axis=1,join="outer")
    df      = df.reset_index()
    
    #Add additional fields
    df["Participant ID"]=username
    df["Date"] = df["Datetime"].map(lambda x: x.date())
    df["Time"] = df["Datetime"].map(lambda x: x.time())

    #Reindex
    df = df.set_index(["Participant ID", "Datetime"])

    #Reset column order
    cols = ["Date","Time","Steps","Heart Rate"]
    df=df[cols]

    #Set missing steps to 0 when HR is defined
    df['Steps'] = df['Steps'].fillna(0) #Set all missing steps to 0
    df.loc[df['Heart Rate'].isnull(), 'Steps'] = np.nan #Reset to nan when hr is null


    #Export to csv
    if(save):
        utils.print_export_statistics(df, 4)
        df.to_csv(os.path.join(directory,filename))

    return(df)
