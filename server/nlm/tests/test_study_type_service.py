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
from nlm.services import StudyTypeService, LogService
from nlm.programlets import ProgramletParameters
from nlm.tasks import nlm_base_hourly_task

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
        # print(self.participant.__dict__)
        # study_type_service.handle_participant_hourly_task(self.participant)
        nlm_base_hourly_task({"minute":1})