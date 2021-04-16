import unittest
from unittest import TestCase

from django.db.utils import IntegrityError

import django
from django.conf import settings
from django.contrib.auth.models import User

from participants.models import Study, Cohort

from .services import NLMService

class NLMServiceTest(TestCase):
    def setUp(self):
        # create test user
        try:
            self.user = User.objects.get(username='user_for_test')
            # previous test has failed
            print('reusing old test user..')
        except User.DoesNotExist:
            # previous test has succeeded
            self.user = User.objects.create(username='user_for_test')            

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
            
    def tearDown(self):
        self.cohort.delete()
        self.study.delete()
        self.user.delete()
        
    #######################################
        
        
    def test_new_service_instance_with_empty_init(self):
        self.assertRaises(TypeError, NLMService)
    
    def test_new_service_instance_with_correct_init(self):
        nlm_service = NLMService(self.user)
    
    def test_new_service_instance_with_correct_init_but_wrong_argument(self):
        self.assertRaises(ValueError, NLMService, None)
    
    def test_assign_cohort_nlm(self):
        nlm_service = NLMService(self.user)
        nlm_service.assign_cohort_to_nlm(self.cohort)
    
    def test_assign_cohort_nlm_with_wrong_argument_1(self):
        nlm_service = NLMService(self.user)
        self.assertRaises(ValueError, nlm_service.assign_cohort_to_nlm, None)
    
    def test_assign_cohort_nlm_with_wrong_argument_2(self):
        nlm_service = NLMService(self.user)
        self.assertRaises(ValueError, nlm_service.assign_cohort_to_nlm, self.study)
        
    def test_assign_cohort_nlm_with_wrong_argument_3(self):
        nlm_service = NLMService(self.user)
        self.assertRaises(ValueError, nlm_service.assign_cohort_to_nlm, self.user)
        
    def test_add_conditionailty_1(self):
        nlm_service = NLMService(self.user)
        name = "Random_50_50"
        description = "take chances of 50:50"
        module = "nlm.conditionality.Random_50_50"
        nlm_service.add_conditionaility(name, description, module)
        nlm_service.remove_conditionaility(name)
        
    def test_add_conditionailty_2(self):
        nlm_service = NLMService(self.user)
        name = "Random_50_50"
        name2 = "Random_50_50_2"
        description = "take chances of 50:50"
        module = "nlm.conditionality.Random_50_50"
        module2 = "nlm.conditionality.Random_50_50_2"
        nlm_service.add_conditionaility(name, description, module)
        self.assertRaises(IntegrityError, nlm_service.add_conditionaility, name, description, module)
        nlm_service.remove_conditionaility(name)
        
    def test_add_conditionailty_3(self):
        nlm_service = NLMService(self.user)
        name = "Random_50_50"
        name2 = "Random_50_50_2"
        description = "take chances of 50:50"
        module = "nlm.conditionality.Random_50_50"
        module2 = "nlm.conditionality.Random_50_50_2"
        nlm_service.add_conditionaility(name, description, module)
        self.assertRaises(IntegrityError, nlm_service.add_conditionaility, name, description, module2)
        nlm_service.remove_conditionaility(name)

    def test_add_conditionailty_4(self):
        nlm_service = NLMService(self.user)
        name = "Random_50_50"
        name2 = "Random_50_50_2"
        description = "take chances of 50:50"
        module = "nlm.conditionality.Random_50_50"
        module2 = "nlm.conditionality.Random_50_50_2"
        nlm_service.add_conditionaility(name, description, module)
        self.assertRaises(IntegrityError, nlm_service.add_conditionaility, name2, description, module)
        nlm_service.remove_conditionaility(name)
        nlm_service.remove_conditionaility(name2)
        
    def test_add_conditionailty_5(self):
        nlm_service = NLMService(self.user)
        name = "Random_50_50"
        name2 = "Random_50_50_2"
        description = "take chances of 50:50"
        module = "nlm.conditionality.Random_50_50"
        module2 = "nlm.conditionality.Random_50_50_2"
        nlm_service.add_conditionaility(name, description, module)
        nlm_service.add_conditionaility(name2, description, module2)
        nlm_service.remove_conditionaility(name)
        nlm_service.remove_conditionaility(name2)
        
    def test_run_conditionality(self):
        nlm_service = NLMService(self.user)
        module = "nlm.conditionality.Random_50_50"
        result = nlm_service.call_conditionality(module)
        