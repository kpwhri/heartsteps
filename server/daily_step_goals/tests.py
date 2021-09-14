from activity_summaries.models import Day
from datetime import datetime

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
    
    
    def test_get_todays_step_goal_1(self):
        
        
        service = StepGoalsService(self.user)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 8).date(), steps=1008)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 9).date(), steps=1009)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 10).date(), steps=1010)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 11).date(), steps=1011)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 12).date(), steps=1012)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 13).date(), steps=1013)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 14).date(), steps=1014) # average of this
        Day.objects.create(user=self.user, date=datetime(2021, 9, 15).date(), steps=1015) #            and this
        Day.objects.create(user=self.user, date=datetime(2021, 9, 16).date(), steps=1016)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 17).date(), steps=1017)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 18).date(), steps=1018)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 19).date(), steps=1019)
        today_step_goal = service.get_step_goal(date=datetime(2021, 9, 20).date())
        
        self.assertEqual(today_step_goal, 1015)

    def test_get_todays_step_goal_2(self):
        service = StepGoalsService(self.user)
        
        Day.objects.create(user=self.user, date=datetime(2021, 9, 13).date(), steps=1013)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 14).date(), steps=1014) 
        Day.objects.create(user=self.user, date=datetime(2021, 9, 15).date(), steps=1015) 
        Day.objects.create(user=self.user, date=datetime(2021, 9, 16).date(), steps=1016) # median = this
        Day.objects.create(user=self.user, date=datetime(2021, 9, 17).date(), steps=1017)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 18).date(), steps=1018)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 19).date(), steps=1019)
        today_step_goal = service.get_step_goal(date=datetime(2021, 9, 20).date())
        
        self.assertEqual(today_step_goal, 1016)


    def test_get_todays_step_goal_3(self):
        service = StepGoalsService(self.user)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 8).date(), steps=1008)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 9).date(), steps=1009)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 10).date(), steps=1010)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 11).date(), steps=1011)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 12).date(), steps=1012)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 13).date(), steps=1013)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 14).date(), steps=1014) # average of this
        Day.objects.create(user=self.user, date=datetime(2021, 9, 15).date(), steps=1015) #            and this
        Day.objects.create(user=self.user, date=datetime(2021, 9, 16).date(), steps=1016)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 17).date(), steps=1017)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 18).date(), steps=1018)
        Day.objects.create(user=self.user, date=datetime(2021, 9, 19).date(), steps=1019)
        
        goal_sequence = service.generate_dump_goal_sequence(date=datetime(2021, 9, 20).date())
        self.assertEqual(goal_sequence, [1615, 1815, 2015, 1615, 1815, 2015])