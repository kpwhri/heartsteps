from datetime import date
from datetime import timedelta

from django.test import TestCase

from .models import Configuration
from .models import BurstPeriod
from .models import User

class TestBurstPeriodGeneration(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user=self.user
        )

    def test_does_not_generate_dates_if_disabled(self):
        self.configuration.enabled = False
        self.configuration.save()
        start = date.today()
        end = date.today() + timedelta(days=self.configuration.interval_length)

        self.configuration.generate_schedule(start, end)

        total_burst_periods = BurstPeriod.objects.filter(user=self.user).count()
        self.assertEqual(total_burst_periods, 0)

    def test_generates_single_burst_period(self):
        start = date.today()
        end = date.today() + timedelta(days=self.configuration.interval_length)

        self.configuration.generate_schedule(start, end)

        total_burst_periods = BurstPeriod.objects.filter(user=self.user).count()
        self.assertEqual(total_burst_periods, 1)

    def test_generates_burst_periods(self):
        number_of_periods = 4
        duration = self.configuration.interval_length * number_of_periods
        start = date.today()
        end = date.today() + timedelta(days=duration)

        self.configuration.generate_schedule(start, end)

        periods = BurstPeriod.objects.filter(user = self.user).all()
        self.assertEqual(len(periods), number_of_periods)
