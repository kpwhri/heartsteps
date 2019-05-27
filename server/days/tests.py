from datetime import date

from django.test import TestCase

from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser

from .models import Day
from .models import User
from .services import DayService

class DayTimezoneTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.account = FitbitAccount.objects.create(fitbit_user="test")
        FitbitAccountUser.objects.create(
            account=self.account,
            user = self.user
        )

    def test_timezone_updated_from_fitbit_day(self):
        other_user = User.objects.create(username="other-user")
        FitbitAccountUser.objects.create(
            account = self.account,
            user = other_user
        )

        FitbitDay.objects.create(
            account = self.account,
            date = date.today(),
            _timezone = "America/New York"
        )

        self.assertEqual(Day.objects.count(), 2)
        day = Day.objects.get(date=date.today(), user=self.user)
        self.assertEqual(day.timezone, "America/New York")
        other_day = Day.objects.get(date=date.today(), user=other_user)
        self.assertEqual(other_day.timezone, "America/New York")

    def test_timezone_can_update_multiple_times(self):
        fitbit_day = FitbitDay.objects.create(
            account = self.account,
            date = date.today(),
            _timezone = "America/New York"
        )

        day = Day.objects.get()
        self.assertEqual(day.timezone, "America/New York")

        fitbit_day._timezone = "America/Los Angeles"
        fitbit_day.save()

        day = Day.objects.get()
        self.assertEqual(day.timezone, "America/Los Angeles")

class DayServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')

    def test_get_timezone_for_today(self):

