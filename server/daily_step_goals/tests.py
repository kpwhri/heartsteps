from freezegun import freeze_time
from activity_summaries.models import Day as ActivitySummaryDay
from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from heartsteps.tests import HeartStepsTestCase

from .services import StepGoalsService
from .models import User

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
    
def create_walk_data(user, start_date, steps):
    for step_index, step in enumerate(steps):
        if step:
            ActivitySummaryDay.objects.create(user=user, date=start_date + timedelta(days=step_index), steps=step)


def get_goals(user, start_date, length):
    service = StepGoalsService(user)
    return_list = []
    for day_index in range(length):
        goal = service.get_goal(start_date + timedelta(days=day_index))
        return_list.append(goal)
    
    return return_list
        

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
        
        with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
            service = StepGoalsService(self.user)
            
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004, 1005]
            )
            
            # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
            goals = get_goals(self.user, datetime(2021, 1, 7).date(), 6)
            self.assertEqual(goals, [1602, 1802, 2002, 1602, 1802, 2002])
        
    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    def test_get_todays_step_goal_2(self, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        
        with freeze_time(lambda: datetime.strptime("2021-01-18 07:09", "%Y-%m-%d %H:%M")):
            service = StepGoalsService(self.user)
            
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004, 1005]
            )
            
            # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
            goals = get_goals(self.user, datetime(2021, 1, 13).date(), 6)
            self.assertEqual(goals, [600, 800, 1000, 600, 800, 1000])

    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    def test_get_todays_step_goal_3(self, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        
        with freeze_time(lambda: datetime.strptime("2021-01-30 07:09", "%Y-%m-%d %H:%M")):
            service = StepGoalsService(self.user)
            
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004, 1005]
            )
            
            # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
            goals = get_goals(self.user, datetime(2021, 1, 13).date(), 6)
            self.assertEqual(goals, [600, 800, 1000, 600, 800, 1000])
    
    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    def test_get_todays_step_goal_4(self, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        
        with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
            service = StepGoalsService(self.user)
            
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, None, 1003, 1004, 1005]
            )
            
            # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
            goals = get_goals(self.user, datetime(2021, 1, 7).date(), 6)
            self.assertEqual(goals, [1603, 1803, 2003, 1603, 1803, 2003])