import pandas as pd
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone
from math import floor

import utils

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

from morning_messages.models import MorningMessage

from walking_suggestions.models import WalkingSuggestionDecision
from collections import defaultdict

def walking_suggestions(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    
    uid = user["uid"]
    username = user["hsid"]

    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.withinday_walking_suggestions.csv'.format(
            username = username
        )

    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return

    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    day_start = np.array([x.start for x in days])
    day_end   = np.array([x.end for x in days])
    day_tz    = [x.timezone for x in days]

    def get_tz_from_datetime(t):
        i=np.argmin(np.abs(day_start-t))
        return pytz.timezone(day_tz[i])

    def localize_datetime(t):
        tz = get_tz_from_datetime(t)
        if(tz is not None):
            return t.astimezone(tz)
        else:
            return pd.NaT

    queryset = WalkingSuggestionDecision.objects.filter(
        user = uid,
        test = False
    ) \
    .order_by('time') \
    .prefetch_rating() \
    .prefetch_weather_forecast() \
    .prefetch_location() \
    .prefetch_notification() \
    .prefetch_unavailable_reasons() \
    .prefetch_message_template(WalkingSuggestionDecision.MESSAGE_TEMPLATE_MODEL)

    df_walking = pd.DataFrame({'Object': [rec for rec in queryset]})

    df_walking["Participant ID"]=username
    df_walking["Datetime"] = df_walking["Object"].map( lambda x: localize_datetime(x.time).replace(tzinfo=None))
    df_walking["Date"] = df_walking["Object"].map( lambda x: localize_datetime(x.time).date())
    df_walking["Time"] = df_walking["Object"].map( lambda x: localize_datetime(x.time).replace(tzinfo=None).time())

    #Add base fields
    base_fields={"imputed":"Imputed",
            "_location":"Location",
            "available":"Available",
            "sedentary":"Sedentary",
            "treated":"Treated",
            "rating":"rating",
            "treatment_probability":"Treatment Probability"}
    for f,n in base_fields.items():
        df_walking[n]=df_walking["Object"].map(lambda x: getattr(x,f))

    #Add unavailable reasons
    df_walking["Unavailable Reasons"] = df_walking["Object"].map(lambda x: x._unavailable_reasons)

    unavailable_reasons={'unreachable':'Unavailable Unreachable',
            'notification-recently-sent':'Unavailable Notification recently sent',
            'not-sedentary':'Unavailable Not sedentary',
            'recently-active':'Unavailable Recently Active',
            'on-vacation':'Unavailable On vacation',
            'no-step-count-data':'Unavailable No step-count data',
            'disabled':'Unavailable Disabled',
            'service-error':'Unavailable Service-error'}

    for f,n in unavailable_reasons.items():
        df_walking[n]=df_walking["Unavailable Reasons"].map(lambda x: f in x)

    #Add weather fields
    df_walking["Weather"] = df_walking["Object"].map(lambda x: x._forecast)

    weather_fields={'precip_probability':"Precipitation Probability",
                    'precip_type':"Precipitation Type",
                    'temperature':"Temperature",
                    'wind_speed':"Wind Speed",
                    'cloud_cover':"Cloud Cover"
                    }
    for f,n in weather_fields.items():
        df_walking[n]=df_walking["Weather"].map(lambda x: getattr(x,f))

    #Add notification fields
    df_walking["Notification Title"]           = df_walking["Object"].map(lambda x: x.notification.title if (x.treated and x.notification is not None) else None)
    df_walking["Notification Body"]            = df_walking["Object"].map(lambda x: x.notification.body if (x.treated and x.notification is not None) else None)
    df_walking["Notification Receipts"]        = df_walking["Object"].map(lambda x: x.notification._message_receipts if (x.treated and x.notification is not None) else None)
    df_walking['Notification Was Sent']        = df_walking["Notification Receipts"].map(lambda x: "sent" in x if x is not None else False)
    df_walking['Notification Was Received']    = df_walking["Notification Receipts"].map(lambda x: "received" in x if x is not None else False)
    df_walking['Notification Was Opened']      = df_walking["Notification Receipts"].map(lambda x: "opened" in x if x is not None else False)
    df_walking['Notification Time Sent']       = df_walking["Notification Receipts"].map(lambda x: localize_datetime(x["sent"]) if (x is not None and "sent" in x) else pd.NaT)
    df_walking['Notification Time Received']   = df_walking["Notification Receipts"].map(lambda x: localize_datetime(x["received"]) if (x is not None and "received" in x) else pd.NaT)
    df_walking['Notification Time Opened']     = df_walking["Notification Receipts"].map(lambda x: localize_datetime(x["opened"]) if (x is not None and "opened" in x) else pd.NaT)

    df_walking=df_walking.drop(labels=["Object","Notification Receipts","Weather","Unavailable Reasons"],axis=1)

    df_walking = df_walking.set_index(["Participant ID","Date"])

    df_walking.to_csv(os.path.join(directory,filename))
