from django.test import TestCase
from bout_planning_notification.models import User, Level
from days.services import DayService
from datetime import datetime, timedelta

class LevelModelTest(TestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test")

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
        