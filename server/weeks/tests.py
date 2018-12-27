
from django.test import TestCase
from django.utils import timezone

from .models import User, Week
from .services import WeekService

class WeeksServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

    def test_create_week(self):
        service = WeekService(user=self.user)

        week = service.create_week()