import unittest
import json
from unittest import TestCase

from django.db.utils import IntegrityError

import django
from django.conf import settings
from django.contrib.auth.models import User

from participants.models import Study, Cohort

from heartsteps.tests import HeartStepsTestCase
from nlm.models import StudyType
from nlm.models import PreloadedLevelSequenceFile
from nlm.services import StudyTypeService, LogService
from dashboard.services import DevService
from nlm.programlets import ProgramletParameters
from nlm.tasks import nlm_base_hourly_task

from django.utils import timezone
import datetime
import pytz

from days.models import Day

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
        
        self.assertRaises(AssertionError, study_type_service.assign_level_sequence, self.participant, None)
    
    def test_assign_level_sequence_2(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertRaises(PreloadedLevelSequenceFile.DoesNotExist, study_type_service.assign_level_sequence, self.participant, "sample_seq")
    
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
        study_type_service.assign_level_sequence(self.participant, "sample_csv")
        
        study_type_service.delete_level_csv("sample_csv")
        
    def test_check_sequence_assignment_1(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        study_type_service.is_level_sequence_assigned(self.participant)
    
    def test_check_sequence_assignment_2(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertFalse(study_type_service.is_level_sequence_assigned(self.participant))
        
    def test_check_sequence_assignment_3(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertFalse(study_type_service.is_level_sequence_assigned(self.participant))
        
        sample_sequence = ["1"] * 5
        sample_sequence_str = ",".join(sample_sequence)
        sample_csv = [sample_sequence_str] * 3
        
        # sample_csv = ['"1","1","1","1","1"',
        #               '"1","1","1","1","1"',
        #               '"1","1","1","1","1"'
        #               ]
        
        study_type_service.upload_level_csv("sample.csv", "sample_csv", sample_csv)
        study_type_service.assign_level_sequence(self.participant, "sample_csv")
        
        self.assertTrue(study_type_service.is_level_sequence_assigned(self.participant))
        
        
        study_type_service.delete_level_csv("sample_csv")

    def test_fetch_todays_level(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertFalse(study_type_service.is_level_sequence_assigned(self.participant))
        
        sample_sequence = [str(StudyTypeService.LEVEL1)] * 5
        sample_sequence_str = ",".join(sample_sequence)
        sample_csv = [sample_sequence_str] * 3
        
        # sample_csv = ['"1","1","1","1","1"',
        #               '"1","1","1","1","1"',
        #               '"1","1","1","1","1"'
        #               ]
        
        study_type_service.upload_level_csv("sample.csv", "sample_csv", sample_csv)
        study_type_service.assign_level_sequence(self.participant, "sample_csv")
        
        self.assertTrue(study_type_service.is_level_sequence_assigned(self.participant))
        
        self.assertEqual(StudyTypeService.LEVEL1, study_type_service.fetch_todays_level(self.participant))
        
        study_type_service.delete_level_csv("sample_csv")
        
        
    def test_is_decision_point_1(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 7, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 10, 1)))
        
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 10, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 10, 1)))
        
    
    def test_is_decision_point_2(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)
        
        Day.objects.create(
            user = self.user,
            date = datetime.date.today(),
            timezone = 'America/Los_Angeles'
        )
        
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 7, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 8, 10, 1, tzinfo=pytz.timezone('US/Pacific'))))
        
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 10, 59, 59)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 0, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 1, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 3, 0)))
        self.assertTrue(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 10, 0)))
        self.assertFalse(study_type_service.is_decision_needed(self.participant, test_time=timezone.datetime(2021, 6, 3, 11, 10, 1)))
        
    def test_random_conditionality(self):
        study_type_service = StudyTypeService(self.study_type_name, self.user)

        self.assertTrue(study_type_service.get_random_conditionality(self.participant, test_value=0))
        self.assertTrue(study_type_service.get_random_conditionality(self.participant, test_value=10))
        self.assertTrue(study_type_service.get_random_conditionality(self.participant, test_value=20))
        self.assertTrue(study_type_service.get_random_conditionality(self.participant, test_value=30))
        self.assertTrue(study_type_service.get_random_conditionality(self.participant, test_value=40))
        self.assertTrue(study_type_service.get_random_conditionality(self.participant, test_value=50))
        self.assertFalse(study_type_service.get_random_conditionality(self.participant, test_value=60))
        self.assertFalse(study_type_service.get_random_conditionality(self.participant, test_value=70))
        self.assertFalse(study_type_service.get_random_conditionality(self.participant, test_value=80))
        self.assertFalse(study_type_service.get_random_conditionality(self.participant, test_value=90))
        self.assertFalse(study_type_service.get_random_conditionality(self.participant, test_value=100))
        