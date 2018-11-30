import pytz
from unittest.mock import patch

from django.test import TestCase, override_settings

@override_settings(PARTICIPANT_NIGHTLY_UPDATE_TIME='2:00')
class NightlyUpdateTest(TestCase):
    pass
