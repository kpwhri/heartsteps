from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APITestCase
from django.urls import reverse

from heartsteps.tests import HeartStepsTestCase

from bout_planning_notification.models import BoutPlanningDecision, User, FirstBoutPlanningTime
from bout_planning_notification.tasks import bout_planning_decision_making, BoutPlanningFlagException
from bout_planning_notification.receivers import FirstBoutPlanningTime_updated
from push_messages.models import Device, Message
from locations.models import Place
from feature_flags.models import FeatureFlags
from participants.models import Study, Cohort, Participant

from freezegun import freeze_time
from datetime import datetime, date
import pytz

from activity_summaries.models import Day

class BoutPlanningDecisionModelTest(HeartStepsTestCase):
    def test_create(self):
        BoutPlanningDecision.create(self.user)
    
    def test_apply_N(self):
        decision = BoutPlanningDecision.create(self.user)
        
        FirstBoutPlanningTime.create(self.user, time="07:00")

        for i in range(0, 10):
            Day.objects.create(user=self.user, date=date(2021, 9, 10+i), steps=4567)
        
        with freeze_time(lambda: datetime.strptime("2021-09-20 07:05", "%Y-%m-%d %H:%M")):
            FeatureFlags.create_or_update(self.user, "bout_planning")
            decision.apply_N()
            
            self.assertEqual(decision.N, False)