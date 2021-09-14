import pytz
from freezegun import freeze_time
import unittest
import json
from unittest.mock import patch
from datetime import datetime
from datetime import date

import django
from django.test import override_settings
from django.db.utils import IntegrityError
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


from days.models import Day
from participants.models import Study, Cohort
from heartsteps.tests import HeartStepsTestCase
from nlm.models import StudyType
from nlm.models import PreloadedLevelSequenceFile
from nlm.services import StudyTypeService, LogService
from dashboard.services import DevService
from nlm.programlets import ProgramletParameters
from nlm.tasks import nlm_base_hourly_task
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from activity_summaries.models import ActivitySummary


@override_settings(WALKING_SUGGESTION_SERVICE_URL='http://example')
class StudyTypeServiceTest(HeartStepsTestCase):
    def setUp(self):
        super().setUp()
        self.study_type_name = "test study type"
    
    #######################################
        
        
    def test_new_service_instance_with_empty_init(self):
        self.assertRaises(TypeError, StudyTypeService)
    
    def test_new_service_instance_with_correct_init(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
    
    def test_new_service_instance_with_correct_init_but_wrong_argument(self):
        self.assertRaises(AssertionError, StudyTypeService, None, None)
    
    def test_assign_cohort_nlm(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        study_type_service.assign_cohort(self.cohort)
        
    def test_assign_cohort_nlm_with_wrong_argument_1(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        self.assertRaises(ValueError, study_type_service.assign_cohort, None)
    
    def test_assign_cohort_nlm_with_wrong_argument_2(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        self.assertRaises(ValueError, study_type_service.assign_cohort, self.study)
        
    def test_assign_cohort_nlm_with_wrong_argument_3(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        self.assertRaises(ValueError, study_type_service.assign_cohort, self.user)
        
    def test_add_conditionailty(self):
        # Try to insert normal trivial conditionality
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        # study_type_service.clear_all_conditionalities()
        name = "always_true_conditionality"
        description = "always return true"
        module_path = "nlm.conditionality.always_true_conditionality"
        study_type_service.add_conditionality(name, description, module_path)
        study_type_service.remove_conditionality(module_path)
        
    def test_run_conditionality(self):
        # try to run individual conditionality
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        module = "nlm.conditionality.always_true_conditionality"
        result = study_type_service.call_conditionality(module)

    def test_run_conditionality_with_logging(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        module = "nlm.conditionality.Random_50_50_log"
        result = study_type_service.call_conditionality(module)
            
    def test_create_conditionality_parameter(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        name = "random with parameterized threshold"
        description = "random with parameterized threshold"
        module_path = "nlm.conditionality.parameterized_conditionality"
        try:
            study_type_service.remove_conditionality(module_path)
        except:
            pass        
        new_conditionality = study_type_service.add_conditionality(name, description, module_path)

        conditionality_parameter_name = "nlm.test.test_conditionality.ramdom.threshold"
        try:
            study_type_service.remove_conditionality_parameter(new_conditionality, conditionality_parameter_name)
        except:
            pass
        study_type_service.set_conditionality_parameter(new_conditionality, conditionality_parameter_name, 0.2)
        study_type_service.remove_conditionality_parameter(new_conditionality, conditionality_parameter_name)
        study_type_service.remove_conditionality(module_path)

    def test_use_conditionality_parameter_with_setting(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        name = "random with parameterized threshold"
        description = "random with parameterized threshold"
        module_path = "nlm.conditionality.parameterized_conditionality"
        try:
            study_type_service.remove_conditionality(module_path)
        except:
            pass     
        new_conditionality = study_type_service.add_conditionality(name, description, module_path)
        
        conditionality_parameter_name = "nlm.test.test_conditionality.ramdom.threshold"
        try:
            study_type_service.remove_conditionality_parameter(new_conditionality, conditionality_parameter_name)
        except:
            pass
        study_type_service.set_conditionality_parameter(new_conditionality, conditionality_parameter_name, 0.2)
        
        
        conditionality_parameter_name2 = "nlm.test.test_conditionality.ramdom.test_str"
        try:
            study_type_service.remove_conditionality_parameter(new_conditionality, conditionality_parameter_name2)
        except:
            pass
        study_type_service.set_conditionality_parameter(new_conditionality, conditionality_parameter_name2, "test string")
        
        
        
        params = ProgramletParameters(
            "Test_Test",
            study_type_service,
            new_conditionality)
        study_type_service.call_conditionality(module_path, parameters=params)
        
        study_type_service.remove_conditionality_parameter(new_conditionality, conditionality_parameter_name)
        study_type_service.remove_conditionality_parameter(new_conditionality, conditionality_parameter_name2)
        study_type_service.remove_conditionality(module_path)
    
    def test_handle_conditionality(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        nlm_base_hourly_task({})
        
    def test_create_preloaded_level_sequence_file(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        sample_sequence = ["1"] * 5
        sample_sequence_str = ",".join(sample_sequence)
        sample_csv = [sample_sequence_str] * 3
        
        # print(sample_csv)
        
        
        study_type_service.upload_level_csv("sample.csv", "sample_csv", sample_csv)
        # dev_service = DevService(self.user)
        # print(dev_service.view_preloaded_seq())
        study_type_service.delete_level_csv("sample_csv")
    
    
    def test_assign_level_sequence_1(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertRaises(AssertionError, study_type_service.assign_level_sequence, self.user, None)
    
    def test_assign_level_sequence_2(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertRaises(PreloadedLevelSequenceFile.DoesNotExist, study_type_service.assign_level_sequence, self.user, "sample_seq")
    
    def test_assign_level_sequence_3(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        sample_sequence = ["1"] * 5
        sample_sequence_str = ",".join(sample_sequence)
        sample_csv = [sample_sequence_str] * 3
        
        # sample_csv = ['"1","1","1","1","1"',
        #               '"1","1","1","1","1"',
        #               '"1","1","1","1","1"'
        #               ]
        
        study_type_service.upload_level_csv("sample.csv", "sample_csv", sample_csv)
        study_type_service.assign_level_sequence(self.user, "sample_csv")
        
        study_type_service.delete_level_csv("sample_csv")
        
    def test_check_sequence_assignment_1(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        study_type_service.is_level_sequence_assigned(self.user)
    
    def test_check_sequence_assignment_2(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertFalse(study_type_service.is_level_sequence_assigned(self.user))
        
    def test_check_sequence_assignment_3(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertFalse(study_type_service.is_level_sequence_assigned(self.user))
        
        sample_sequence = ["1"] * 5
        sample_sequence_str = ",".join(sample_sequence)
        sample_csv = [sample_sequence_str] * 3
        
        # sample_csv = ['"1","1","1","1","1"',
        #               '"1","1","1","1","1"',
        #               '"1","1","1","1","1"'
        #               ]
        
        study_type_service.upload_level_csv("sample.csv", "sample_csv", sample_csv)
        study_type_service.assign_level_sequence(self.user, "sample_csv")
        
        self.assertTrue(study_type_service.is_level_sequence_assigned(self.user))
        
        
        study_type_service.delete_level_csv("sample_csv")

    # study type service is obsolete
    # def test_fetch_todays_level(self):
    #     study_type_service = StudyTypeService(self.study_type_name, self.user)
        
    #     self.assertFalse(study_type_service.is_level_sequence_assigned(self.user))
        
    #     sample_sequence = [str(StudyTypeService.LEVEL1)] * 5
    #     sample_sequence_str = ",".join(sample_sequence)
    #     sample_csv = [sample_sequence_str] * 3
        
    #     # sample_csv = ['"1","1","1","1","1"',
    #     #               '"1","1","1","1","1"',
    #     #               '"1","1","1","1","1"'
    #     #               ]
        
    #     study_type_service.upload_level_csv("sample.csv", "sample_csv", sample_csv)
    #     study_type_service.assign_level_sequence(self.user, "sample_csv")
        
    #     self.assertTrue(study_type_service.is_level_sequence_assigned(self.user))
        
    #     self.assertEqual(StudyTypeService.LEVEL1, study_type_service.fetch_todays_level(self.user))
        
    #     study_type_service.delete_level_csv("sample_csv")
        
        
    def test_is_decision_point_1(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 7, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 10, 1)))
        
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 10, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 10, 1)))
        
    
    def test_is_decision_point_2(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        Day.objects.create(
            user = self.user,
            date = date(2021, 6, 2),
            timezone = 'America/Los_Angeles'
        )
        
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 7, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 8, 10, 1, tzinfo=pytz.timezone('US/Pacific'))))
        
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 10, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.user, test_time=datetime(2021, 6, 3, 11, 10, 1)))
        
    def test_random_conditionality(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)

        self.assertTrue(study_type_service.get_random_conditionality(self.user, test_value=0))
        self.assertTrue(study_type_service.get_random_conditionality(self.user, test_value=10))
        self.assertTrue(study_type_service.get_random_conditionality(self.user, test_value=20))
        self.assertTrue(study_type_service.get_random_conditionality(self.user, test_value=30))
        self.assertTrue(study_type_service.get_random_conditionality(self.user, test_value=40))
        self.assertTrue(study_type_service.get_random_conditionality(self.user, test_value=50))
        self.assertFalse(study_type_service.get_random_conditionality(self.user, test_value=60))
        self.assertFalse(study_type_service.get_random_conditionality(self.user, test_value=70))
        self.assertFalse(study_type_service.get_random_conditionality(self.user, test_value=80))
        self.assertFalse(study_type_service.get_random_conditionality(self.user, test_value=90))
        self.assertFalse(study_type_service.get_random_conditionality(self.user, test_value=100))
    
    @patch('nlm.services.StudyTypeService.get_decision_point_gap')
    @patch('nlm.services.StudyTypeService.get_decision_point_expiration_window')
    @patch('nlm.services.StudyTypeService.get_first_decision_point_hour')
    @patch('nlm.services.StudyTypeService.get_last_day_achieved')
    @patch('nlm.services.StudyTypeService.get_today_steps')
    @patch('daily_step_goals.services.StepGoalsService.get_step_goal')
    def test_need_conditionality(self, 
                                 mock_get_step_goal, 
                                 mock_get_today_steps, 
                                 mock_get_last_day_achieved,
                                 mock_get_first_decision_point_hour,
                                 mock_get_decision_point_expiration_window,
                                 mock_get_decision_point_gap):
        
        Day.objects.create(
            user = self.user,
            date = date(2021, 6, 10),
            timezone = 'America/Los_Angeles'
        )
        
        study_type_service = StudyTypeService(self.study_type_name, self.user)

        # non-relevant mocking
        mock_get_first_decision_point_hour.return_value = 8
        mock_get_decision_point_expiration_window.return_value = 10
        mock_get_decision_point_gap.return_value = 3


        # first decision point => totally depends on the previous goal achievement (invert the last_day_achieved))
        mock_get_step_goal.return_value = 8000
        mock_get_today_steps.return_value = 0
        mock_get_last_day_achieved.return_value = False
        with freeze_time(lambda: datetime.strptime("2021-06-14 08:05-0700", "%Y-%m-%d %H:%M%z")):
            self.assertTrue(study_type_service.get_need_conditionality(self.user))
            
        mock_get_last_day_achieved.return_value = True
        with freeze_time(lambda: datetime.strptime("2021-06-14 07:55-0700", "%Y-%m-%d %H:%M%z")):
            self.assertFalse(study_type_service.get_need_conditionality(self.user))
        
        with freeze_time(lambda: datetime.strptime("2021-06-14 08:05-0700", "%Y-%m-%d %H:%M%z")):
            self.assertFalse(study_type_service.get_need_conditionality(self.user))


        
        # second and later decision points => Prorated Goals = (Elapsed Hours) * (Daily Goal) / 12. returns whether if current step is larger than prorated goals
        mock_get_step_goal.return_value = 8000
        mock_get_today_steps.return_value = 0
        with freeze_time(lambda: datetime.strptime("2021-06-14 11:00-0700", "%Y-%m-%d %H:%M%z")):
            self.assertTrue(study_type_service.get_need_conditionality(self.user))

        mock_get_today_steps.return_value = 4000
        with freeze_time(lambda: datetime.strptime("2021-06-14 11:00-0700", "%Y-%m-%d %H:%M%z")):
            self.assertFalse(study_type_service.get_need_conditionality(self.user))
            

        # before decision window
        mock_get_last_day_achieved.return_value = False
        with freeze_time(lambda: datetime.strptime("2021-06-14 07:55-0700", "%Y-%m-%d %H:%M%z")):
            self.assertTrue(study_type_service.get_need_conditionality(self.user))
        
        mock_get_last_day_achieved.return_value = True
        with freeze_time(lambda: datetime.strptime("2021-06-14 07:55-0700", "%Y-%m-%d %H:%M%z")):
            self.assertFalse(study_type_service.get_need_conditionality(self.user))

        # after decision window => Prorated Goals = (Daily Goal). returns whether if current step is larger than prorated goals
        mock_get_step_goal.return_value = 8000
        mock_get_today_steps.return_value = 7900
        with freeze_time(lambda: datetime.strptime("2021-06-14 22:00-0700", "%Y-%m-%d %H:%M%z")):
            self.assertTrue(study_type_service.get_need_conditionality(self.user))

        mock_get_today_steps.return_value = 9000
        with freeze_time(lambda: datetime.strptime("2021-06-14 22:00-0700", "%Y-%m-%d %H:%M%z")):
            self.assertFalse(study_type_service.get_need_conditionality(self.user))
            
    @patch('nlm.services.StudyTypeService.get_steps')
    @patch('nlm.services.StudyTypeService.get_step_goal')
    def test_get_last_day_achieved_1(self,
                                   mock_get_step_goal,
                                   mock_get_steps):
        # Test simple logic only
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        mock_get_step_goal.return_value = 8000
        mock_get_steps.return_value = 123
        with freeze_time(lambda: datetime.strptime("2021-06-14 12:34-0700", "%Y-%m-%d %H:%M%z")):
            self.assertFalse(study_type_service.get_last_day_achieved(self.user))
            
        mock_get_steps.return_value = 8213
        with freeze_time(lambda: datetime.strptime("2021-06-14 12:34-0700", "%Y-%m-%d %H:%M%z")):
            self.assertTrue(study_type_service.get_last_day_achieved(self.user))
    
    def create_fitbit_account(self):
        self.fitbit_account = FitbitAccount.objects.create(
            fitbit_user='test'
        )
        FitbitAccountUser.objects.create(
            account = self.fitbit_account,
            user = self.user
        )
    
    def create_fitbit_walk_day(self, day, step_count=500):
        FitbitDay.objects.create(
            account = self.fitbit_account,
            date = day,
            step_count = step_count
        )
    
    def delete_fitbit_walk_day(self, day):
        FitbitDay.objects.filter(
            account = self.fitbit_account,
            date = day
        ).all().delete()
        ActivitySummary.objects.filter(
            user = self.user
        ).all().delete()

    def test_get_steps(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        self.create_fitbit_account()
        
        self.create_fitbit_walk_day(
            day = date(2018,10,10),
            step_count = 400
        )
        self.assertEqual(study_type_service.get_steps(self.user, date=date(2018,10,10)), 400)
        
        self.delete_fitbit_walk_day(
            day = date(2018,10,10)
        )
        
    @patch('daily_step_goals.services.StepGoalsService.get_step_goal')
    def test_get_step_goal(self, mock_get_step_goal):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        mock_get_step_goal.return_value = 3456
        self.assertEqual(study_type_service.get_step_goal(self.user), 3456)