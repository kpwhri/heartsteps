import pprint

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
from datetime import datetime, date, time, timedelta
import pytz
import random

from activity_summaries.models import Day
from fitbit_api.models import FitbitAccountUser, FitbitAccount
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.services import FitbitStepCountService
            
class BoutPlanningDecisionModelTest(HeartStepsTestCase):
    def test_create(self):
        BoutPlanningDecision.create(self.user)
    
    @patch('daily_step_goals.services.StepGoalsService.get_goal')
    def test_apply_N_1(self, mock_get_goal):
        mock_get_goal.return_value = 8000
        decision = self.apply_N_case(True)
        self.assertEqual(decision.N, False)
    
    @patch('daily_step_goals.services.StepGoalsService.get_goal')
    def test_apply_N_2(self, mock_get_goal):
        mock_get_goal.return_value = 8000
        decision = self.apply_N_case(False)
        self.assertEqual(decision.N, True)

    @patch('daily_step_goals.services.StepGoalsService.get_goal')
    def test_apply_N_3(self, mock_get_goal):
        mock_get_goal.return_value = 8000
        decision = self.apply_N_case(True, False)
        self.assertEqual(decision.N, False)
    
    @patch('daily_step_goals.services.StepGoalsService.get_goal')
    def test_apply_N_4(self, mock_get_goal):
        mock_get_goal.return_value = 8000
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
            with freeze_time(lambda: datetime.strptime("2021-09-20 07:09", "%Y-%m-%d %H:%M")):
                FeatureFlags.create_or_update(self.user, "bout_planning")
                decision.apply_N()
        else:
            with freeze_time(lambda: datetime.strptime("2021-09-20 10:05", "%Y-%m-%d %H:%M")):
                FeatureFlags.create_or_update(self.user, "bout_planning")
                decision.apply_N()
        return decision

    def test_apply_O_1(self):
        today = date(2021, 9, 14)
        
        account = self.create_fitbit_account()
        
        self.fake_fitbit_minutes(today, account)
        self.fake_fitbit_minutes(today, account, hour=9)
        self.fake_fitbit_minutes(today, account, hour=11)
        self.fake_fitbit_minutes(today, account, hour=13)
        
        step_count_service = FitbitStepCountService(self.user)
        
        step_data_list = step_count_service.get_all_step_data_list_between(
            datetime.combine(today, time(0,0)).astimezone(pytz.UTC), 
            datetime.combine(today+timedelta(days=1), time(0,0)).astimezone(pytz.UTC)
            )
        
        step_data_list = step_count_service.get_all_step_data_list_between(
            datetime.combine(today, time(7,0)).astimezone(pytz.UTC), 
            datetime.combine(today, time(14,0)).astimezone(pytz.UTC)
            )
    
    
    def test_apply_O_2(self):
        start_day = date(2021, 9, 8)
        
        account = self.create_fitbit_account()
        
        for i in range(0, 10):
            self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=9)
            self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=11)
            self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=13)
            self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=15)
            
        FirstBoutPlanningTime.create(self.user, "07:00")
        self.participant.study_start_date = date(2021, 9, 5)
        
        decision = BoutPlanningDecision.create(self.user)
        with freeze_time(lambda: datetime.strptime("2021-09-20 07:08", "%Y-%m-%d %H:%M")):
            decision.apply_O()
            self.assertEqual(decision.O, False)
        # pprint.pprint(decision.data)
        
    def test_apply_O_3(self):
        start_day = date(2021, 9, 8)
        
        account = self.create_fitbit_account()
        
        for i in range(0, 10):
            # self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=9)
            self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=11)
            self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=13)
            self.fake_fitbit_minutes(start_day + timedelta(days=1) * i, account, hour=15)
            
        FirstBoutPlanningTime.create(self.user, "07:00")
        self.participant.study_start_date = date(2021, 9, 5)
        
        decision = BoutPlanningDecision.create(self.user)
        with freeze_time(lambda: datetime.strptime("2021-09-20 07:07", "%Y-%m-%d %H:%M")):
            decision.apply_O()
            self.assertEqual(decision.O, False)

    def create_fitbit_account(self):
        account = FitbitAccount.objects.create(
            fitbit_user = 'test'
        )
        FitbitAccountUser.create_or_update(
            account = account,
            user = self.user
        )
        
        return account

    def fake_fitbit_minutes(self, today, account, hour=7, minute=5, duration=10, steps_base=100, steps_randmax=0):
        for i in range(0, duration):
            FitbitMinuteStepCount.objects.create(
                account=account,
                steps=steps_base + random.randint(0, steps_randmax),
                time=datetime.combine(today, time(hour, minute+i)).astimezone(pytz.UTC)
            )
    
    # def test_fetch_walk_data(self):
    #     decision = BoutPlanningDecision.create(self.user)
        
    #     fitbit_account = FitbitAccount.objects.create(fitbit_user="abcd")
    #     FitbitAccountUser.objects.create(account=fitbit_account, user=self.user)
    #     decision.apply_O()
        