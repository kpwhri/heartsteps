from datetime import date, datetime
from unittest.mock import patch
import pytz

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import User, Week
from .services import WeekService

class WeeksServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")

    def test_create_week(self):
        service = WeekService(user=self.user)

        week = service.create_week()

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

        self.assertEqual(first_week.number, 0)
        self.assertEqual(second_week.number, 1)

    def test_moves_overlapping_weeks(self):
        week0 = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 1),
            end_date = date(2018, 12, 9)
        )
        week1 = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 10),
            end_date = date(2018, 12, 16)
        )
        week2 = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 17),
            end_date = date(2018, 12, 23)
        )
        week3 = Week.objects.create(
            user = self.user,
            start_date = date(2018, 12, 24),
            end_date = date(2018, 12, 27)
        )
        # Other user to make sure doesnt move
        week_other = Week.objects.create(
            user = User.objects.create(username="other"),
            start_date = date(2018, 12, 17),
            end_date = date(2018, 12, 20)
        )

        week1.end_date = date(2018, 12, 20)
        week1.save()

        week2 = Week.objects.get(uuid=week2.uuid)
        self.assertEqual(week2.start_date, date(2018, 12, 21))
        self.assertEqual(week2.end_date, date(2018, 12, 27))
        # Week 3 should stay same amount of days different (3 days)
        week3 = Week.objects.get(uuid=week3.uuid)
        self.assertEqual(week3.start_date, date(2018, 12, 28))
        self.assertEqual(week3.end_date, date(2018, 12, 31))
        #Following shouldn't move
        week0 = Week.objects.get(uuid=week0.uuid)
        self.assertEqual(week0.start_date, date(2018, 12, 1))
        self.assertEqual(week0.end_date, date(2018, 12, 9))
        week_other = Week.objects.get(uuid=week_other.uuid)
        self.assertEqual(week_other.start_date, date(2018, 12, 17))
        self.assertEqual(week_other.end_date, date(2018, 12, 20))

class WeekViewsTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.client.force_authenticate(user=self.user)

        timezone_patch = patch.object(timezone, 'now')
        self.now = timezone_patch.start()
        self.now.return_value = datetime(2019, 1, 6, 8).astimezone(pytz.UTC)
        self.addCleanup(timezone_patch.stop)

        Week.objects.create(
            user = self.user,
            start_date = date(2019, 1, 1),
            end_date = date(2019, 1, 3),
            number = 0
        )
        Week.objects.create(
            user = self.user,
            start_date = date(2019, 1, 4),
            end_date = date(2019, 1, 10),
            number = 1
        )
        Week.objects.create(
            user = self.user,
            start_date = date(2019, 1, 11),
            end_date = date(2019, 1, 17),
            number = 2
        )

    def test_get_current_week(self):
        response = self.client.get(reverse('weeks-current'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['start'], '2019-01-04')

    def test_get_week_2(self):
        response = self.client.get(reverse('weeks', kwargs={
            'week_number': 2
        }))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 2)
        self.assertEqual(response.data['start'], '2019-01-11')

    def test_get_next_week(self):
        response = self.client.get(reverse('weeks', kwargs={
            'week_number': 3
        }))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('weeks-next', kwargs={
            'week_number': 2
        }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 3)
        self.assertEqual(response.data['start'], '2019-01-18')
        self.assertEqual(response.data['end'], '2019-01-24')

        response = self.client.get(reverse('weeks', kwargs={
            'week_number': 3
        }))
        self.assertEqual(response.status_code, 200)