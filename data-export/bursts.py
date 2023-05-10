from collections import defaultdict

import pandas as pd
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone
from math import floor
from logs import localize_time
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

def export_burst_survey(user,queryset,survey_type,questions,DEBUG=True):

    """
    Construct dataframe from a burst survey data model 
    """

    uid = user["uid"]
    username = user["hsid"]

    #Get survey indicators
    #Get days, timezones, and survey dweel time
    days      = Day.objects.filter(user_id=uid).order_by("date").all()
    if not days:
        print("EMPTY DAY QUERY")
    tz_lookup = {x.date: pytz.timezone(x.timezone) for x in days}
    ndt=utils.estimate_notification_dwell_times(uid)

    # Get survey objects
    df = pd.DataFrame({'Object': [x for x in queryset]})

    df["Datetime"] = df['Object'].map(lambda x: localize_time(x.created, tz_lookup))
    
    df["Survey Probability"] = df['Object'].map(lambda x: x.decision.treatment_probability if hasattr(x, 'decision') and x.decision and x.decision.treatment_probability else 1)

    #Lookup notifications and map receipts
    notification_lookup = utils.get_survey_notifications(uid, survey_type)

    df["receipts"] = df['Object'].map(lambda x: notification_lookup[x.uuid]._message_receipts if x.uuid in notification_lookup.keys() else [])

    df['Notification Was Sent']      = df["receipts"].map(lambda x: "sent" in x)
    df['Notification Was Received']  = df["receipts"].map(lambda x: "received" in x)
    df['Notification Was Opened']    = df["receipts"].map(lambda x: "opened" in x)
    df['Notification Time Sent']     = df["receipts"].map(lambda x: localize_time(x["sent"], tz_lookup) if "sent" in x else pd.NaT)
    df['Notification Time Received'] = df["receipts"].map(lambda x: localize_time(x["received"], tz_lookup) if "received" in x else pd.NaT)
    df['Notification Time Opened']   = df["receipts"].map(lambda x: localize_time(x["opened"], tz_lookup) if "opened" in x else pd.NaT)

    #Survey time details
    sot = df['Object'].map(lambda x: get_survey_open_time(str(notification_lookup[x.uuid].uuid),tz_lookup,ndt)) #opend time
    sat = df['Object'].map(lambda x: localize_time(x.updated,tz_lookup) if x.answered else pd.NaT) #answered time
    df["Survey Was Opened"]   = sot.map(lambda x: x is not pd.NaT) 
    df["Survey Was Answered"] = df["Object"].map(lambda x: x.answered)
    df["Survey Time Opened"]  =sot
    df["Survey Time Answered"]=sat

    time_spent_l = []
    for at,ot in zip(sot, sat):
        time_spent_l.append(at-ot)
    time_spent = pd.Series(data=time_spent_l)
    
    df['Survey Time Spent Answering'] = time_spent.map(lambda x: np.round(x.total_seconds(),1) if (x is not None and x is not np.nan and not pd.isnull(x)) else x)

    #Get survey answers dictionary and map
    df["answers"]=df["Object"].map(lambda x: x.get_answers())
    for f,n in questions.items():
        df[n]=df["answers"].map(lambda x: x[f] if f in x else None)

    #Set index and drop extra columns
    df["Particiant ID"]=username

    #Map time fields to strings
    time_fields = ['Datetime','Notification Time Sent',
                   'Notification Time Received',
                   'Notification Time Opened',
                   "Survey Time Opened",
                   "Survey Time Answered"]
    for f in time_fields:
        df[f] = df[f].map(to_time_str)

    df = df.set_index(["Particiant ID", "Datetime"]) 
    df = df.drop(labels=["answers","Object","receipts"],axis=1)

    return df


def export_burst_walking_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from WalkingSuggestionSurvey data model and export to csv
    """

    uid = user["uid"]
    username = user["hsid"]

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

    queryset = WalkingSuggestionSurvey.objects.filter(user_id=uid).order_by('created', 'updated').all()

    if not queryset:
        print("EMPTY QUERY: WalkingSuggestionSurvey")

    questions={'busyness':'Busyness',
                'commitment':'Commitment',
                'relaxed':'Relaxed',
                'tense':'Tense',
                'energetic':'Energetic', 
                'fatigued':'Fatigued', 
                'happy':'Happy', 
                'sad':'Sad', 
                'stressed':'Stressed', 
                'opportunity':'Opportunity'
    }

    survey_type = 'Walking Suggestion Survey'

    df = export_burst_survey(user,queryset,survey_type,questions,DEBUG=DEBUG)

    utils.verify_column_names(df, os.path.join(directory, filename))
    #utils.print_export_statistics(df, 22)
    df.to_csv(os.path.join(directory, filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

    return


def export_burst_activity_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from ActivitySurvey data model and export to csv
    """

    uid = user["uid"]
    username = user["hsid"]

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


    queryset = ActivitySurvey.objects.filter(user_id=uid).order_by('created', 'updated').all()
    if not queryset:
        print("EMPTY QUERY: ActivitySurvey")

    questions={'enjoyment':"Enjoyment of Activities",
        'fit':"Fit with Routine", 
        'social_support':"Social Support", 
        'intrinsic_motivation':"Intrinsic Motivation", 
        'extrinsic_motivation':"Extrinsic Motivation"
    }

    survey_type = 'Activity Survey'

    df = export_burst_survey(user,queryset,survey_type,questions,DEBUG=DEBUG)

    #utils.print_export_statistics(df, 17)
    utils.verify_column_names(df, os.path.join(directory, filename))
    df.to_csv(os.path.join(directory, filename))

    if(DEBUG):
        import code
        code.interact(local=dict(globals(), **locals()))

    return

#Get localized time the survey page was opened
def get_survey_open_time(notification_uuid,tz_lookup,ndt):
    id = str(notification_uuid)
    if id in ndt:
        return localize_time(ndt[id]["opened"],tz_lookup)
    else:
        return pd.NaT

def to_time_str(x):
    if( x is not np.nan and x is not None and not pd.isnull(x)):
        return x.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return x