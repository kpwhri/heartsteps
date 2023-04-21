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

    
import code
code.interact(local=dict(globals(), **locals()))

pst=pytz.timezone("America/Los_Angeles")
utc=pytz.timezone("UTC")

x1=datetime.datetime.strptime('8/27/2021', "%m/%d/%Y")
x2=datetime.datetime.strptime('8/31/2021', "%m/%d/%Y")

user=333;allPageViews=PageView.objects.filter(user_id=user).order_by("time").filter(time__lte=utc.localize(x2), time__gte=utc.localize(x1))

for p in allPageViews: print(p.time.astimezone(pst), p.uri)