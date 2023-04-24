from collections import defaultdict

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

from walking_suggestion_surveys.models import WalkingSuggestionSurvey
from activity_surveys.models import ActivitySurvey, Decision

def export_burst_walking_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from WalkingSuggestionSurvey data model and export to csv
    """

    uid = user["uid"]
    username = user["hsid"]

    if DEBUG:
        print("  Exporting burst walking survey data for: ", username)

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.burst_walking_survey.csv'.format(
            username=username
        )

    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return


    import code
    code.interact(local=dict(globals(), **locals()))

    u = WalkingSuggestionSurvey.objects.filter(user_id=uid).order_by('created', 'updated').all()

    questions = ['busyness', 'commitment', 'relaxed', 'tense', 'energetic', 'fatigued', 'happy', 'sad', 'stressed', 'opportunity']

    data={}
    data["Participant ID"]=[]
    data["Time Created"]=[]
    data["Time Completed"]=[]
    data["Answered"]=[]
    for q in questions:
        data[q.title()]=[]

    for i,s in enumerate(u):
        data["Participant ID"].append(username)
        data["Time Created"].append(s.created)
        data["Time Completed"].append(s.updated if s.answered else np.nan)
        data["Answered"].append(s.answered)
        answers = s.get_answers()
        for q in questions:
            data[q.title()].append(answers[q] if q in answers else np.nan)

    df = pd.DataFrame(data)

    print(f"   Total answers {df['Answered'].sum()}")
    #print(df)

    df.to_csv(os.path.join(directory,filename))

def export_burst_activity_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from ActivitySurvey data model and export to csv
    """

    uid = user["uid"]
    username = user["hsid"]

    if DEBUG:
        print("  Exporting burst activity survey data for: ", username)

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.burst_activity_survey.csv'.format(
            username=username
        )

    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    #Get survey indicators
    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}
    ndt=utils.estimate_notification_dwell_times(uid)

    # ActivitySurvey has Decision foreign key
    activity_query = ActivitySurvey.objects.filter(user_id=uid).order_by('created', 'updated').all()
    #decision_query = Decision.objects.filter(user_id=uid).order_by('created', 'updated')

    df = pd.DataFrame({'Object': [x for x in activity_query]})

    df["Datetime"] = df['Object'].map(lambda x: localize_time(x.created, tz_lookup))
    df["Treatment Probability"] = df['Object'].map(lambda x: x.decision.treatment_probability)

    #Notification details
    df["receipts"] = df['Object'].map(lambda x: x.decision.notification.get_message_receipts())

    df['Notification Was Sent']      = df["receipts"].map(lambda x: "sent" in x)
    df['Notification Was Received']  = df["receipts"].map(lambda x: "received" in x)
    df['Notification Was Opened']    = df["receipts"].map(lambda x: "opened" in x)
    df['Notification Time Sent']     = df["receipts"].map(lambda x: localize_time(x["sent"], tz_lookup) if "sent" in x else pd.NaT)
    df['Notification Time Received'] = df["receipts"].map(lambda x: localize_time(x["received"], tz_lookup) if "received" in x else pd.NaT)
    df['Notification Time Opened']   = df["receipts"].map(lambda x: localize_time(x["opened"], tz_lookup) if "opened" in x else pd.NaT)

    #Survey time details
    asot = df['Object'].map(lambda x: get_survey_open_time(x,tz_lookup,ndt))
    asat = df['Object'].map(lambda x: localize_time(x.updated,tz_lookup) if x.answered else pd.NaT)
    df["Survey Was Opened"]   = asot.map(lambda x: x is not pd.NaT) 
    df["Survey Was Answered"] = df["Object"].map(lambda x: x.answered)
    df["Survey Opened Time"]  =asot
    df["Survey Answered Time"]=asat
    df['Survey Time Spent Answering'] = (asat-asot).map(lambda x: np.round(x.total_seconds(),1) if (x is not None and x is not np.nan and not pd.isnull(x)) else x)

    #Get survey answers dictionary and map
    df["answers"]=df["Object"].map(lambda x: x.get_answers())
    answer_fields={'enjoyment':"Enjoyment of Activities",
        'fit':"Fit with Routine", 
        'social_support':"Social Support", 
        'intrinsic_motivation':"Intrinsic Motivation", 
        'extrinsic_motivation':"Extrinsic Motivation"
    }
    for f,n in answer_fields.items():
        df[n]=df["answers"].map(lambda x: x[f] if f in x else None)

    #Set index and drop extra columns
    df["Particiant ID"]=username

    #Map time fields to strings
    time_fields = ['Notification Time Sent',
                   'Notification Time Received',
                   'Notification Time Opened',
                   "Survey Opened Time",
                   "Survey Answered Time"]
    for f in time_fields:
        df[f] = df[f].map(to_time_str)

    df = df.set_index(["Particiant ID", "Datetime"]) 
    df = df.drop(labels=["answers","Object","receipts"],axis=1)

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

#Get localized time the survey page was opened
def get_survey_open_time(activity,tz_lookup,ndt):
    id = str(activity.decision.notification.uuid)
    if id in ndt:
        return localize_time(ndt[id]["opened"],tz_lookup)
    else:
        return pd.NaT

def to_time_str(x):
    if( x is not np.nan and x is not None and not pd.isnull(x)):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return x