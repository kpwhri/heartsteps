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

    # ActivitySurvey has Decision foreign key
    activity_query = ActivitySurvey.objects.filter(user_id=uid).order_by('created', 'updated').all()
    #decision_query = Decision.objects.filter(user_id=uid).order_by('created', 'updated')

    questions = ['enjoyment', 'fit', 'social_support', 'intrinsic_motivation', 'extrinsic_motivation']

    activity_dict = defaultdict(list)

    for _,activity in enumerate(activity_query):

        # ActivitySurvey fields
        activity_dict["Participant ID"].append(username)
        activity_dict["Time Created"].append(activity.created)
        activity_dict["Time Completed"].append(activity.updated if activity.answered else np.nan)
        activity_dict["Answered"].append(activity.answered)

        # ActivitySurvey.Decision fields
        activity_dict["Decision Created"].append(activity.decision.created)
        activity_dict["Decision Updated"].append(activity.decision.updated)

        # Decision.Message fields
        activity_dict["Message Sent"].append(activity.decision.notification.sent if activity.decision.notification else np.nan)
        activity_dict["Message Received"].append(activity.decision.notification.received if activity.decision.notification else np.nan)
        activity_dict["Message Opened"].append(activity.decision.notification.opened if activity.decision.notification else np.nan)
        activity_dict["Message Engaged"].append(activity.decision.notification.engaged if activity.decision.notification else np.nan)

        answers = activity.get_answers()
        for q in questions:
            # confirm an answer exists and it is not None
            activity_dict[q.title()].append(answers[q] if q in answers and answers[q] else np.nan)

    df = pd.DataFrame(activity_dict)

    print(f"   Total answers {df['Answered'].sum()}")

    df.to_csv(os.path.join(directory, filename))
