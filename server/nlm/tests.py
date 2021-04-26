import unittest
from unittest import TestCase

from django.db.utils import IntegrityError

import django
from django.conf import settings
from django.contrib.auth.models import User

from participants.models import Study, Cohort

from .models import StudyType
from .services import StudyTypeService, LogService

class StudyTypeServiceTest(TestCase):
    def setUp(self):
        # create test user
        self.user, newuser = User.objects.get_or_create(username='user_for_test')         

        # create test study
        try:
            self.study = Study.objects.get(name='study_for_test')
            # previous test has failed
            print('reusing old test study..')
        except Study.DoesNotExist:
            study_name = "study_for_test"
            contact_name = "Debugger"
            contact_number = "8581234567"
            baseline_period = 7
            self.study = Study.objects.create(name=study_name, 
                                            contact_name=contact_name,
                                            contact_number=contact_number,
                                            baseline_period=baseline_period  
                                            )
            self.study.admins.set([self.user])
        
        # create test cohort
        try:
            self.cohort = Cohort.objects.filter(study=self.study).first()
            if self.cohort:
                # previous test has failed
                print('reusing old test cohort..')
            else:
                raise Cohort.DoesNotExist
        except Cohort.DoesNotExist:
            cohort_name = "cohort_for_test"
            study_length = 365
            export_data = False   
            self.cohort = Cohort.objects.create(
                                            study=self.study,
                                            name=cohort_name,
                                            study_length=study_length,
                                            export_data=export_data
                                            )   
        self.study_type_name = "test study type"
            
    def tearDown(self):
        self.cohort.delete()
        self.study.delete()
        self.user.delete()
        
    #######################################
        
        
    def test_new_service_instance_with_empty_init(self):
        self.assertRaises(TypeError, StudyTypeService)
    
    def test_new_service_instance_with_correct_init(self):
        study_type_service = StudyTypeService(self.user, self.study_type_name)
    
    def test_new_service_instance_with_correct_init_but_wrong_argument(self):
        self.assertRaises(ValueError, StudyTypeService, None, None)
    
    def test_assign_cohort_nlm(self):
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        study_type_service.assign_cohort(self.cohort)
        
    def test_assign_cohort_nlm_with_wrong_argument_1(self):
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        self.assertRaises(ValueError, study_type_service.assign_cohort, None)
    
    def test_assign_cohort_nlm_with_wrong_argument_2(self):
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        self.assertRaises(ValueError, study_type_service.assign_cohort, self.study)
        
    def test_assign_cohort_nlm_with_wrong_argument_3(self):
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        self.assertRaises(ValueError, study_type_service.assign_cohort, self.user)
        
    def test_add_conditionailty_1(self):
        # Try to insert normal trivial conditionality
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        name = "always_true_conditionality"
        description = "always return true"
        module_path = "nlm.conditionality.always_true_conditionality"
        study_type_service.add_conditionaility(name, description, module_path)
        study_type_service.remove_conditionaility(name)
        
    def test_add_conditionailty_2(self):
        # Try to insert same conditionality twice : causes exception
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        name = "always_true_conditionality"
        description = "always return true"
        module = "nlm.conditionality.always_true_conditionality"
        study_type_service.add_conditionaility(name, description, module)
        self.assertRaises(IntegrityError, study_type_service.add_conditionaility, name, description, module)
        study_type_service.remove_conditionaility(name)
        
    def test_add_conditionailty_3(self):
        # Try to insert two conditionalities with same names, and different module path : causes exception
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        name = "always_true_conditionality"
        name2 = "always_true_conditionality_2"
        description = "always return true"
        module = "nlm.conditionality.always_true_conditionality"
        module2 = "nlm.conditionality.always_true_conditionality_2"
        study_type_service.add_conditionaility(name, description, module)
        self.assertRaises(IntegrityError, study_type_service.add_conditionaility, name, description, module2)
        study_type_service.remove_conditionaility(name)

    def test_add_conditionailty_4(self):
        # Try to insert two conditionalities with different names, and same module path : causes exception
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        name = "always_true_conditionality"
        name2 = "always_true_conditionality_2"
        description = "always return true"
        module = "nlm.conditionality.always_true_conditionality"
        study_type_service.add_conditionaility(name, description, module)
        self.assertRaises(IntegrityError, study_type_service.add_conditionaility, name2, description, module)
        study_type_service.remove_conditionaility(name)
        study_type_service.remove_conditionaility(name2)
        
    def test_add_conditionailty_5(self):
        # Try to insert two conditionalities with different names, and different module path : no exception
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        name = "always_true_conditionality"
        name2 = "always_true_conditionality_2"
        description = "always return true"
        module = "nlm.conditionality.always_true_conditionality"
        module2 = "nlm.conditionality.always_true_conditionality_2"
        study_type_service.add_conditionaility(name, description, module)
        study_type_service.add_conditionaility(name2, description, module2)
        study_type_service.remove_conditionaility(name)
        study_type_service.remove_conditionaility(name2)
        
    def test_run_conditionality(self):
        # try to run individual conditionality
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        module = "nlm.conditionality.always_true_conditionality"
        result = study_type_service.call_conditionality(module)

    def test_run_conditionality_with_logging(self):
        study_type_service = StudyTypeService(self.user, self.study_type_name)
        module = "nlm.conditionality.Random_50_50_log"
        result = study_type_service.call_conditionality(module)
    
    def test_log(self):
        log_service = LogService(subject_name="nlm.test")
        
        import time
        
        log_service.log()
        time.sleep(0.500)
        log_service.log()
    
    def test_dump_all_logging(self):
        log_service = LogService(subject_name="nlm.test")
        
        print(log_service.dump())
        
    def test_clear_all_logging(self):
        log_service = LogService(subject_name="nlm.test")
        
        import time
        
        log_service.clear()        
        log_service.log()
        time.sleep(0.200)
        log_service.log()
        
        log_service.clear()  