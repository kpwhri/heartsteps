from datetime import date
from datetime import datetime
import pytz
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

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
            _timezone = "America/New_York"
        )

        self.assertEqual(Day.objects.count(), 2)
        day = Day.objects.get(date=date.today(), user=self.user)
        self.assertEqual(day.timezone, "America/New_York")
        other_day = Day.objects.get(date=date.today(), user=other_user)
        self.assertEqual(other_day.timezone, "America/New_York")

    def test_timezone_can_update_multiple_times(self):
        fitbit_day = FitbitDay.objects.create(
            account = self.account,
            date = date.today(),
            _timezone = "America/New_York"
        )

        day = Day.objects.get()
        self.assertEqual(day.timezone, "America/New_York")

        fitbit_day._timezone = "America/Los_Angeles"
        fitbit_day.save()

        day = Day.objects.get()
        self.assertEqual(day.timezone, "America/Los_Angeles")

class DayServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            date_joined = datetime(2019, 5, 3, 14, 14).astimezone(pytz.UTC)    
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 5, 3),
            timezone = "America/Los_Angeles"
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 5, 6),
            timezone = "America/New_York"
        )

    def test_creates_not_already_created(self):
        service = DayService(username="test")

        dt = service.get_datetime_at(datetime(2019,5,5,12,5).astimezone(pytz.UTC))
        self.assertEqual(dt.strftime('%Y-%m-%d %H:%M'), '2019-05-05 05:05')

        day = Day.objects.get(
            user = self.user,
            date = date(2019, 5, 5)
        )
        self.assertEqual(day.timezone, "America/Los_Angeles")

    def test_get_timezone_at(self):
        service = DayService(username="test")

        timezone = service.get_timezone_at(datetime(2019, 5, 5, 15).astimezone(pytz.UTC))
        self.assertEqual(timezone, pytz.timezone("America/Los_Angeles"))
        
        timezone = service.get_timezone_at(datetime(2019, 5, 6, 20).astimezone(pytz.UTC))
        self.assertEqual(timezone, pytz.timezone("America/New_York"))

    def test_get_datetime_at(self):
        service = DayService(username="test")

        dt = service.get_datetime_at(datetime(2019, 5, 5, 20, 25).astimezone(pytz.UTC))
        self.assertEqual(dt.strftime('%Y-%m-%d %H:%M'), '2019-05-05 13:25')

        dt = service.get_datetime_at(datetime(2019, 5, 6, 9, 15).astimezone(pytz.UTC))
        self.assertEqual(dt.strftime('%Y-%m-%d %H:%M'), '2019-05-06 05:15')

    def test_get_date_at(self):
        service = DayService(username="test")

        d = service.get_date_at(datetime(2019, 5, 5, 4, 23).astimezone(pytz.UTC))
        self.assertEqual(d.strftime('%Y-%m-%d'), '2019-05-04')

        d = service.get_date_at(datetime(2019, 5, 6, 7, 23).astimezone(pytz.UTC))
        self.assertEqual(d.strftime('%Y-%m-%d'), '2019-05-06')

    @patch.object(timezone, 'now', return_value=datetime(2019, 5, 5, 17, 5).astimezone(pytz.UTC))
    def test_current_timezone(self, timezone):
        service = DayService(username="test")

        tz = service.get_current_timezone()

        self.assertEqual(tz, pytz.timezone('America/Los_Angeles'))

    @patch.object(timezone, 'now', return_value=datetime(2019, 5, 5, 17, 5).astimezone(pytz.UTC))
    def test_current_datetime(self, timezone):
        service = DayService(username="test")

        dt = service.get_current_datetime()

        self.assertEqual(dt.strftime('%Y-%m-%d %H:%M'), "2019-05-05 10:05")

    @patch.object(timezone, 'now', return_value=datetime(2019, 5, 5, 17, 5).astimezone(pytz.UTC))
    def test_current_date(self, timezone):
        service = DayService(username="test")

        dt = service.get_current_date()

        self.assertEqual(dt.strftime('%Y-%m-%d'), "2019-05-05")
