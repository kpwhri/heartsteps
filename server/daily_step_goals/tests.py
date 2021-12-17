from activity_summaries.models import Day as ActivitySummaryDay
from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from heartsteps.tests import HeartStepsTestCase

from .services import StepGoalsService
from .models import User, StepGoalPRBScsv

from participants.models import Study, Cohort, Participant

class ModelStepGoals(HeartStepsTestCase):
    pass

class ModelStepGoalsPRBScsv(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.study = Study.objects.create()
        self.cohort = Cohort.objects.create(study=self.study)
        self.participant = Participant.objects.create(user=self.user, cohort=self.cohort)
    
    def tearDown(self):
        self.user.delete()
    
    def test_PRBS_1(self):
        StepGoalPRBScsv.objects.create(cohort=self.cohort, PRBS_text='0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0')
        prbs_list = StepGoalPRBScsv.get_seq(self.cohort)
        
        self.assertEqual(prbs_list, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

class ServiceStepGoalsService(HeartStepsTestCase):
    def test_create_service_1(self):
        self.assertRaises(TypeError, StepGoalsService)
    
    def test_create_service_2(self):
        self.assertRaises(AssertionError, StepGoalsService, None)
    
    def test_create_service_3(self):
        service = StepGoalsService(self.user)
    
    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    def test_get_todays_step_goal_1(self, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        
        service = StepGoalsService(self.user)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 8).date(), steps=1008)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 9).date(), steps=1009)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 10).date(), steps=1010)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 11).date(), steps=1011)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 12).date(), steps=1012)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 13).date(), steps=1013)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 14).date(), steps=1014) 
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 15).date(), steps=1015) 
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 16).date(), steps=1016) 
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 17).date(), steps=1017)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 18).date(), steps=1018)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 19).date(), steps=1019)
        
        today_step_goal = service.get_goal(datetime(2021, 9, 20).date())
        self.assertEqual(today_step_goal, 1815)

    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    def test_get_todays_step_goal_2(self, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        service = StepGoalsService(self.user)
        
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 13).date(), steps=1013)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 14).date(), steps=1014) 
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 15).date(), steps=1015) 
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 16).date(), steps=1016) 
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 17).date(), steps=1017)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 18).date(), steps=1018)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 19).date(), steps=1019)
        
        today_step_goal = service.get_goal(datetime(2021, 9, 20).date())
        self.assertEqual(today_step_goal, 1815)

    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    def test_get_todays_step_goal_3(self, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        
        service = StepGoalsService(self.user)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 8).date(), steps=1008)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 9).date(), steps=1009)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 10).date(), steps=1010)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 11).date(), steps=1011)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 12).date(), steps=1012)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 13).date(), steps=1013)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 14).date(), steps=1014)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 15).date(), steps=1015)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 16).date(), steps=1016) 
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 17).date(), steps=1017)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 18).date(), steps=1018)
        ActivitySummaryDay.objects.create(user=self.user, date=datetime(2021, 9, 19).date(), steps=1019)
        
        goal = service.get_goal(datetime(2021, 9, 20).date())
        self.assertEqual(goal, 1815)