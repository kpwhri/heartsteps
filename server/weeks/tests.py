from datetime import date

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
