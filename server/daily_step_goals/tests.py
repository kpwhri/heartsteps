from freezegun import freeze_time
from activity_summaries.models import Day as ActivitySummaryDay
from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from heartsteps.tests import HeartStepsTestCase

from .services import StepGoalsService
from .models import StepGoalSequenceBlock, User

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
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004]
            )
            
            # use PRBS as '0.3, 0.4, 0.5, 0.6, 0.7'
            # ActivityDay will be used from 1000~1004 (5 days) => median: 1002
            goals = get_goals(self.user, datetime(2021, 1, 6).date(), 5)
            self.assertEqual(goals, [10000, 10000, 10000, 10000, 10000])

    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    @patch('participants.services.ParticipantService.is_baseline_complete')
    def test_get_todays_step_goal_1_no_baseline(self, mock_is_baseline_complete, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        mock_is_baseline_complete.return_value = True
        
        with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004]
            )
            
            # use PRBS as '0.3, 0.4, 0.5, 0.6, 0.7'
            # ActivityDay will be used from 1000~1004 (5 days) => median: 1002
            goals = get_goals(self.user, datetime(2021, 1, 6).date(), 5)
            self.assertEqual(goals, [3200, 3600, 4000, 4400, 4800])
    
    
    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    @patch('participants.services.ParticipantService.is_baseline_complete')
    def test_get_todays_step_goal_2(self, mock_is_baseline_complete, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        mock_is_baseline_complete.return_value = True
        
        with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            StepGoalSequenceBlock.objects.create(cohort=self.cohort,
                                                 seq_block="0.1,0.2,0.3,0.4,0.5,0.6,0.7\n0.2,0.3,0.4,0.5,0.6,0.7,0.8"
                                                 )
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004, 1005, 1006]
            )
            
            # use PRBS as '0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7'
            # ActivityDay will be used from 1000~1006 (7 days) => median: 1003
            goals = get_goals(self.user, datetime(2021, 1, 8).date(), 7)
            self.assertEqual(goals, [2400, 2800, 3200, 3600, 4000, 4400, 4800])
    
    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    @patch('participants.services.ParticipantService.is_baseline_complete')
    def test_get_todays_step_goal_2_2(self, mock_is_baseline_complete, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        mock_is_baseline_complete.return_value = True
        
        with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            StepGoalSequenceBlock.objects.create(cohort=self.cohort,
                                                 seq_block="0.1,0.2,0.3,0.4,0.5,0.6,0.7\n0.2,0.3,0.4,0.5,0.6,0.7,0.8"
                                                 )
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[5000, 5001, 5002, 5003, 5004, 5005, 5006]
            )
            
            # use PRBS as '0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7'
            # ActivityDay will be used from 1000~1006 (7 days) => median: 1003
            goals = get_goals(self.user, datetime(2021, 1, 8).date(), 7)
            self.assertEqual(goals, [5403, 5803, 6203, 6603, 7003, 7403, 7803])
            
    @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    @patch('participants.services.ParticipantService.is_baseline_complete')
    def test_get_todays_step_goal_3(self, mock_is_baseline_complete, mock_update_fitbit_device_with_new_goal):
        mock_update_fitbit_device_with_new_goal.return_value = None
        mock_is_baseline_complete.return_value = True
        
        with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
            self.participant.study_start_date = datetime(2021, 1, 1).date()
            self.participant.save()
            
            self.participant2.study_start_date = datetime(2021, 1, 1).date()
            self.participant2.save()
            
            StepGoalSequenceBlock.objects.create(cohort=self.cohort,
                                                 seq_block="0.1,0.2,0.3,0.4,0.5,0.6,0.7\n0.2,0.3,0.4,0.5,0.6,0.7,0.8"
                                                 )
            
            create_walk_data(
                user=self.user,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004, 1005, 1006]
            )
            
            # use PRBS as '0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7'
            # ActivityDay will be used from 1000~1006 (7 days) => median: 1003
            goals = get_goals(self.user, datetime(2021, 1, 8).date(), 7)
            self.assertEqual(goals, [2400, 2800, 3200, 3600, 4000, 4400, 4800])
            
            
            create_walk_data(
                user=self.user2,
                start_date=datetime(2021, 1, 1).date(),
                steps=[1000, 1001, 1002, 1003, 1004, 1005, 1006]
            )
            
            # use PRBS as '0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8'
            # ActivityDay will be used from 1000~1006 (7 days) => median: 1003
            goals2 = get_goals(self.user2, datetime(2021, 1, 8).date(), 7)
            self.assertEqual(goals2, [2800, 3200, 3600, 4000, 4400, 4800, 5200])
            


            
    # @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    # def test_get_todays_step_goal_1(self, mock_update_fitbit_device_with_new_goal):
    #     mock_update_fitbit_device_with_new_goal.return_value = None
        
    #     with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
    #         service = StepGoalsService(self.user)
            
    #         self.participant.study_start_date = datetime(2021, 1, 1).date()
    #         self.participant.save()
            
    #         create_walk_data(
    #             user=self.user,
    #             start_date=datetime(2021, 1, 1).date(),
    #             steps=[1000, 1001, 1002, 1003, 1004, 1005]
    #         )
            
    #         # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
    #         goals = get_goals(self.user, datetime(2021, 1, 7).date(), 6)
    #         self.assertEqual(goals, [1602, 1802, 2002, 1602, 1802, 2002])
        
    # @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    # def test_get_todays_step_goal_2(self, mock_update_fitbit_device_with_new_goal):
    #     mock_update_fitbit_device_with_new_goal.return_value = None
        
    #     with freeze_time(lambda: datetime.strptime("2021-01-18 07:09", "%Y-%m-%d %H:%M")):
    #         service = StepGoalsService(self.user)
            
    #         self.participant.study_start_date = datetime(2021, 1, 1).date()
    #         self.participant.save()
            
    #         create_walk_data(
    #             user=self.user,
    #             start_date=datetime(2021, 1, 1).date(),
    #             steps=[1000, 1001, 1002, 1003, 1004, 1005]
    #         )
            
    #         # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
    #         goals = get_goals(self.user, datetime(2021, 1, 13).date(), 6)
    #         self.assertEqual(goals, [600, 800, 1000, 600, 800, 1000])

    # @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    # def test_get_todays_step_goal_3(self, mock_update_fitbit_device_with_new_goal):
    #     mock_update_fitbit_device_with_new_goal.return_value = None
        
    #     with freeze_time(lambda: datetime.strptime("2021-01-30 07:09", "%Y-%m-%d %H:%M")):
    #         service = StepGoalsService(self.user)
            
    #         self.participant.study_start_date = datetime(2021, 1, 1).date()
    #         self.participant.save()
            
    #         create_walk_data(
    #             user=self.user,
    #             start_date=datetime(2021, 1, 1).date(),
    #             steps=[1000, 1001, 1002, 1003, 1004, 1005]
    #         )
            
    #         # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
    #         goals = get_goals(self.user, datetime(2021, 1, 13).date(), 6)
    #         self.assertEqual(goals, [600, 800, 1000, 600, 800, 1000])
    
    # @patch('daily_step_goals.tasks.update_fitbit_device_with_new_goal')
    # def test_get_todays_step_goal_4(self, mock_update_fitbit_device_with_new_goal):
    #     mock_update_fitbit_device_with_new_goal.return_value = None
        
    #     with freeze_time(lambda: datetime.strptime("2021-01-07 07:09", "%Y-%m-%d %H:%M")):
    #         service = StepGoalsService(self.user)
            
    #         self.participant.study_start_date = datetime(2021, 1, 1).date()
    #         self.participant.save()
            
    #         create_walk_data(
    #             user=self.user,
    #             start_date=datetime(2021, 1, 1).date(),
    #             steps=[1000, 1001, None, 1003, 1004, 1005]
    #         )
            
    #         # use PRBS as '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
    #         goals = get_goals(self.user, datetime(2021, 1, 7).date(), 6)
    #         self.assertEqual(goals, [1603, 1803, 2003, 1603, 1803, 2003])