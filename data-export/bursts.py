
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

    u = WalkingSuggestionSurvey.objects.filter(user_id=username).order_by('created', 'updated').all()

    df = pd.DataFrame({'Object': u})
    df['Survey Time'] = df['Object'].map(lambda x: x.created)
    df['Completed Time'] = df['Object'].map(lambda x: x.updated if x.answered else np.nan)
    df['Answered'] = df['Object'].map(lambda x: bool(x.answered))
    #df['Burst Period 1'] = df['Object'].map(lambda x: bool(x.created > b1 and x.created < (b1+timedelta(days=8)))
    #df['Burst Period 2'] = df['Object'].map(lambda x: bool(x.created > b2 and x.created < (b2+timedelta(days=8))))
    #df['Burst Period 3'] = df['Object'].map(lambda x: bool(x.created > b3 and x.created < (b3+timedelta(days=8))))
    #df['Burst Period 4'] = df['Object'].map(lambda x: bool(x.created > b4 and x.created < (b4+timedelta(days=8))))
    for q in questions.keys():
        df[q] = df['Object'].map(lambda x: x.get_answers()[q] if q in x.get_answers() else np.nan) 

