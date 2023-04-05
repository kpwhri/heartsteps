
import pandas as pd
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone
from math import floor

import code

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

from walking_suggestion_surveys.models import * 

def export_burst_walking_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from MorningMessage data model and export to csv

    Reference task: export_morning_message_survey in server/morning_messages/tasks.py
    """

    uid = user["uid"]
    username = user["hsid"]

    print(uid,username)

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


    #import code
    #code.interact(local=dict(globals(), **locals()))

    u = WalkingSuggestionSurvey.objects.filter(user_id=uid).order_by('created', 'updated').all()

    questions = ['busyness', 'commitment', 'relaxed', 'tense', 'energetic', 'fatigued', 'happy', 'sad', 'stressed', 'opportunity']

    data={}
    data["created"]=[]
    data["completed"]=[]
    data["answered"]=[]
    for q in questions:
        data[q]=[] 

    for i,s in enumerate(u):
        print(i)
        data["created"].append(s.created)
        data["completed"].append(s.updated if s.answered else np.nan)
        data["answered"].append(s.answered)
        answers = s.get_answers()
        for q in questions:
            data[q].append(answers[q] if q in answers else np.nan)

    df = pd.DataFrame(data)
    df["Participant ID"] = username

    print(df)
