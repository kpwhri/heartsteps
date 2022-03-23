from django.test import TestCase
from bout_planning_notification.models import User, Level
from days.services import DayService
from datetime import datetime, timedelta

from participants.models import Participant
from participants.models import Cohort, Study

class LevelModelTest(TestCase):
    def setUp(self):
        """Create testing user"""

        # study_start_date = datetime(year=2019, month=1, day=1)
        enrollment_date = datetime(year=2019, month=1, day=5)
        self.user = User.objects.create(username="test")
        self.study = Study.objects.create(name="test study", baseline_period=2)
        self.cohort = Cohort.objects.create(study=self.study, name="test cohort")
        self.participant = Participant.objects.create(cohort=self.cohort, study_start_date=enrollment_date, user=self.user)

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()

    def test_get_1(self):
        level = Level.get(self.user)
        
        self.assertEqual(level.level, Level.FULL)
        
    def test_get_2(self):
        Level.create(self.user, Level.RANDOM)
        level = Level.get(self.user)
        
        self.assertEqual(level.level, Level.RANDOM)
    
    def test_get_3(self):
        day_service = DayService(self.user)
        
        today = day_service.get_current_date()
        yesterday = today - timedelta(days=1)
        
        Level.create(self.user, Level.RECOVERY, yesterday)
        Level.create(self.user, Level.NO, today)
        
        level_yesterday = Level.get(self.user, yesterday)
        level_today = Level.get(self.user, today)
        
        self.assertEqual(level_yesterday.level, Level.RECOVERY)
        self.assertEqual(level_today.level, Level.NO)
        