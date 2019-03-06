from datetime import date, datetime
from unittest.mock import patch
import pytz

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from rest_framework.test import APITestCase

from activity_summaries.models import Day
from locations.services import LocationService

from .models import User, Week
from .services import WeekService

class WeeksModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

    def test_correctly_numbers_weeks(self):
        first_week = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 1),
            end_date = date(2018, 12, 2)
        )
        second_week = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 3),
            end_date = date(2018, 12, 4)
        )

        self.assertEqual(first_week.number, 1)
        self.assertEqual(second_week.number, 2)
    
    def test_sets_goal(self):
        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 4),
            end_date = date(2019, 3, 10)
        )

        self.assertEqual(week.goal, 20)
    
    def test_activity_in_week_sets_goal(self):
        Day.objects.create(
            user = self.user,
            date = date(2019, 3, 2),
            total_minutes = 15
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 2, 27),
            total_minutes = 7
        )

        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 4),
            end_date = date(2019, 3, 10)
        )

        self.assertEqual(week.goal, 40)

    def test_goal_not_over_150(self):
        Day.objects.create(
            user = self.user,
            date = date(2019, 3, 2),
            total_minutes = 150
        )
        Day.objects.create(
            user = self.user,
            date = date(2019, 2, 27),
            total_minutes = 70
        )

        week = Week.objects.create(
            user = self.user,
            start_date = date(2019, 3, 4),
            end_date = date(2019, 3, 10)
        )

        self.assertEqual(week.goal, 150)

class WeeksServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

        timezone_patch = patch.object(LocationService, 'get_current_timezone')
        self.current_timezone = timezone_patch.start()
        self.current_timezone.return_value = pytz.timezone('Etc/GMT-8')
        self.addCleanup(timezone_patch.stop)

    @patch.object(timezone, 'now')
    def test_initialize_weeks(self, now):
        now.return_value = pytz.UTC.localize(datetime(2019,2,28))
        self.user.date_joined = datetime(2019,2,1).astimezone(pytz.UTC)
        service = WeekService(user=self.user)

        service.update_weeks()
        
        week = service.get_current_week()
        self.assertEqual(week.number, 5)
        #assert first day of week is a monday
        self.assertEqual(week.start_date.weekday(), 0)
        #assert last day of week is a sunday
        self.assertEqual(week.end_date.weekday(), 6)

class WeekViewsTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            date_joined = datetime(2018, 12, 5).astimezone(pytz.UTC)
        )
        self.client.force_authenticate(user=self.user)

        timezone_patch = patch.object(timezone, 'now')
        self.now = timezone_patch.start()
        self.now.return_value = datetime(2019, 1, 6, 8).astimezone(pytz.UTC)
        self.addCleanup(timezone_patch.stop)

        location_service_patch = patch.object(LocationService, 'get_current_timezone')
        self.current_timezone = location_service_patch.start()
        self.current_timezone.return_value = pytz.UTC
        self.addCleanup(location_service_patch.stop)

        service = WeekService(self.user)
        service.update_weeks()

    def test_get_current_week(self):
        response = self.client.get(reverse('weeks-current'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 5)
        self.assertEqual(response.data['start'], '2018-12-31')
        self.assertEqual(response.data['end'], '2019-01-06')

    def test_get_week_2(self):
        response = self.client.get(reverse('weeks', kwargs={
            'week_number': 2
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 2)
        self.assertEqual(response.data['start'], '2018-12-10')
        self.assertEqual(response.data['end'], '2018-12-16')

    def test_get_next_week(self):
        response = self.client.get(reverse('weeks-next'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 6)
        self.assertEqual(response.data['start'], '2019-01-07')
        self.assertEqual(response.data['end'], '2019-01-13')


    def test_update_week_goal(self):
        response = self.client.post(reverse('weeks-current'), {
            'goal': 23,
            'confidence': 0.21
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 5)
        self.assertEqual(response.data['goal'], 23)
        self.assertEqual(response.data['confidence'], 0.21)

        service = WeekService(self.user)
        current_week = service.get_current_week()
        self.assertEqual(current_week.goal, 23)
        self.assertEqual(current_week.confidence, 0.21)

    def test_update_next_week_goal(self):
        response = self.client.post(reverse('weeks-next'), {
            'goal': 500,
            'confidence': 0.001
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 6)
        self.assertEqual(response.data['goal'], 500)
        self.assertEqual(response.data['confidence'], 0.001)

    def test_update_week_error(self):
        response = self.client.post(reverse('weeks-current'), {})

        self.assertEqual(response.status_code, 400)
