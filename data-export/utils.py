import os, sys, code

def setup():

    EXPORT_DIR    = os.environ["EXPORT_DIR"] 
    HS_SERVER_DIR = os.environ["HS_SERVER_DIR"] 
    DEBUG         = False

    print(f"Configuration - EXPORT_DIR: {EXPORT_DIR}")
    print(f"Configuration - HS_SERVER_DIR: {EXPORT_DIR}")

    sys.path.append(HS_SERVER_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

    from django.conf import settings
    import django
    django.setup()

#Must all setup before importing django modules
setup()

from datetime import datetime,  date, timedelta, timezone
from math import floor

#from celery import shared_task
from django.utils import timezone
#from django.conf import settings
#from django.core import serializers

#from adherence_messages.tasks import export_daily_metrics
#from anti_sedentary.tasks import export_anti_sedentary_decisions
#from anti_sedentary.tasks import export_anti_sedentary_service_requests
from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.models import FitbitActivity

#from fitbit_activities.tasks import export_fitbit_data
#from fitbit_activities.tasks import export_missing_fitbit_data
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Location
from locations.models import Place
#from locations.services import LocationService
#from locations.tasks import export_location_count_csv
#from locations.tasks import update_location_categories
#from morning_messages.tasks import export_morning_message_survey
#from morning_messages.tasks import export_morning_messages
from push_messages.models import Message as PushMessage
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
#from walking_suggestions.tasks import export_walking_suggestion_decisions
#from walking_suggestions.tasks import export_walking_suggestion_service_requests
#from watch_app.tasks import export_step_count_records_csv
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

import pandas as pd
import progressbar
import pytz
import numpy as np
