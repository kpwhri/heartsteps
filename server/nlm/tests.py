import unittest
from unittest import TestCase

import django
from django.conf import settings
from django.contrib.auth.models import User

from participants.models import Cohort

from .services import NLMService

# Create your tests here.

class NLMServiceTest(TestCase):
    def setUp(self):
        try:
            self.user = User.objects.get(username='user_for_test')
            # previous test has failed
            print('reusing old test user..')
        except User.DoesNotExist:
            # previous test has succeeded
            print('creating new test user..')
            self.user = User.objects.create(username='user_for_test')            

    def test_new_service_instance_with_empty_init(self):
        self.assertRaises(TypeError, NLMService)
    
    def test_new_service_instance_with_correct_init(self):
        nlm_service = NLMService(self.user)
    
    def test_new_service_instance_with_correct_init_but_wrong_argument(self):
        self.assertRaises(ValueError, NLMService, None)
    
    def tearDown(self):
        print('deleting the test user..')
        self.user.delete()