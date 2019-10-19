import pytz
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User

from daily_tasks.models import DailyTask
from locations.services import LocationService
from walking_suggestion_times.signals import suggestion_times_updated
from watch_app.signals import step_count_updated

from walking_suggestions.models import Configuration
from walking_suggestions.models import SuggestionTime
from walking_suggestions.tasks import nightly_update

