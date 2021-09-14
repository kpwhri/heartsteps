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
from fitbit_api.models import FitbitAccountUser, FitbitAccount
from fitbit_activities.models import FitbitMinuteStepCount
            
class BoutPlanningDecisionModelTest(HeartStepsTestCase):
    def test_create(self):
        BoutPlanningDecision.create(self.user)
    
    def test_apply_N_1(self):
        decision = self.apply_N_case(True)
        self.assertEqual(decision.N, False)
    
    def test_apply_N_2(self):
        decision = self.apply_N_case(False)
        self.assertEqual(decision.N, True)

    def test_apply_N_3(self):
        decision = self.apply_N_case(True, False)
        self.assertEqual(decision.N, False)
    
    def test_apply_N_4(self):
        decision = self.apply_N_case(False, False)
        self.assertEqual(decision.N, True)


    def apply_N_case(self, step_over, morning=True):
        decision = BoutPlanningDecision.create(self.user)
        
        FirstBoutPlanningTime.create(self.user, time="07:00")

        for i in range(0, 9):
            Day.objects.create(user=self.user, date=date(2021, 9, 10+i), steps=4567)
        
        if step_over:
            if morning:
                Day.objects.create(user=self.user, date=date(2021, 9, 19), steps=8000)
            else:
                Day.objects.create(user=self.user, date=date(2021, 9, 20), steps=8000)
        else:
            if morning:
                Day.objects.create(user=self.user, date=date(2021, 9, 19), steps=1000)
            else:
                Day.objects.create(user=self.user, date=date(2021, 9, 20), steps=1000)
        
        if morning:
            with freeze_time(lambda: datetime.strptime("2021-09-20 07:05", "%Y-%m-%d %H:%M")):
                FeatureFlags.create_or_update(self.user, "bout_planning")
                decision.apply_N()
        else:
            with freeze_time(lambda: datetime.strptime("2021-09-20 10:05", "%Y-%m-%d %H:%M")):
                FeatureFlags.create_or_update(self.user, "bout_planning")
                decision.apply_N()
        return decision

    # def test_apply_O_1(self):
    #     pass
    
    # def test_fetch_walk_data(self):
    #     decision = BoutPlanningDecision.create(self.user)
        
    #     fitbit_account = FitbitAccount.objects.create(fitbit_user="abcd")
    #     FitbitAccountUser.objects.create(account=fitbit_account, user=self.user)
    #     decision.apply_O()
        