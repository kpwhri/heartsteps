from django.test import TestCase
from heartsteps.tests import HeartStepsTestCase

from .services import StepGoalsService

class ModelStepGoals(HeartStepsTestCase):
    pass

class ServiceStepGoalsService(HeartStepsTestCase):
    def test_create_service_1(self):
        self.assertRaises(TypeError, StepGoalsService)
    
    def test_create_service_2(self):
        self.assertRaises(AssertionError, StepGoalsService, None)
    
    def test_create_service_3(self):
        service = StepGoalsService(self.user)
    
    
    def test_get_todays_step_goal_1(self):
        service = StepGoalsService(self.user)
        
        today_step_goal = service.get_today_step_goal()