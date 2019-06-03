import pytz
from unittest.mock import patch
from datetime import datetime
from datetime import date
from datetime import timedelta

from django.test import TestCase
from django.test import override_settings
from django.contrib.auth.models import User

from fitbit import Fitbit

from fitbit_api.models import FitbitAccount, FitbitAccountUser
from fitbit_api.services import FitbitClient
from fitbit_api.signals import update_date as fitbit_update_date

from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitActivity
from fitbit_activities.services import FitbitDayService
from fitbit_activities.tasks import update_fitbit_data

class TestBase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            date_joined = datetime(2018,2,1).astimezone(pytz.UTC)
        )
        self.account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            user = self.user,
            account = self.account
        )

        timezone_patch = patch.object(FitbitClient, 'get_timezone')
        self.timezone = timezone_patch.start()
        self.timezone.return_value = pytz.timezone('UTC')
        self.addCleanup(timezone_patch.stop)

class FitbitDayUpdates(TestBase):

    def setUp(self):
        super().setUp()

        activities_patch = patch.object(FitbitClient, 'get_activities')
        self.addCleanup(activities_patch.stop)
        self.get_activities = activities_patch.start()
        self.get_activities.return_value = []

        heart_rate_patch = patch.object(FitbitClient, 'get_heart_rate')
        self.addCleanup(heart_rate_patch.stop)
        self.get_heart_rate = heart_rate_patch.start()
        self.get_heart_rate.return_value = []

        step_count_patch = patch.object(FitbitClient, 'get_steps')
        self.addCleanup(step_count_patch.stop)
        self.get_steps = step_count_patch.start()
        self.get_steps.return_value = []

        distance_patch = patch.object(FitbitClient, 'get_distance')
        self.addCleanup(distance_patch.stop)
        self.get_distance = distance_patch.start()
        self.get_distance.return_value = []

    def testUpdateTaskCreatesDay(self):
        self.timezone.return_value = pytz.timezone('Poland')
        self.get_steps.return_value = [{
            'time': '10:10:00',
            'value': 20
        }]
        self.get_distance.return_value = [{
            'time': '10:10:00',
            'value': 0.123
        }]

        update_fitbit_data(fitbit_user=self.account.fitbit_user, date_string="2018-02-14")

        fitbit_day = FitbitDay.objects.get(account=self.account)
        self.assertEqual(fitbit_day.get_timezone().zone, "Poland")
        self.assertEqual(fitbit_day.date.strftime('%Y-%m-%d'), "2018-02-14")
        self.assertEqual(fitbit_day.step_count, 20)
        self.assertEqual(fitbit_day.distance, 0.123)

    @override_settings(FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES=20)
    def test_updates_wore_fitbit(self):
        heart_rates = []
        for offset in range(20):
            time = datetime(2018, 2, 14, 11) + timedelta(minutes=offset)
            heart_rates.append({
                'time': time.strftime('%H:%M:00'),
                'value': 70
            })
        self.get_heart_rate.return_value = heart_rates

        update_fitbit_data(fitbit_user=self.account.fitbit_user, date_string="2018-02-14")

        fitbit_day = FitbitDay.objects.get(account=self.account)
        self.assertTrue(fitbit_day.wore_fitbit)

    @override_settings(FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES=20)
    def test_wore_fitbit_out_of_range(self):
        heart_rates = []
        for offset in range(20):
            time = datetime(2018, 2, 14, 23) + timedelta(minutes=offset)
            heart_rates.append({
                'time': time.strftime('%H:%M:00'),
                'value': 70
            })
        self.get_heart_rate.return_value = heart_rates

        update_fitbit_data(fitbit_user=self.account.fitbit_user, date_string="2018-02-14")

        fitbit_day = FitbitDay.objects.get(account=self.account)
        self.assertFalse(fitbit_day.wore_fitbit)

    def test_did_not_wear_fitbit(self):

        update_fitbit_data(fitbit_user=self.account.fitbit_user, date_string="2019-02-14")

        fitbit_day = FitbitDay.objects.get(account=self.account)
        self.assertFalse(fitbit_day.wore_fitbit)

class FitbitStepUpdates(TestBase):

    def setUp(self):
        super().setUp()

        fitbit_patch = patch.object(Fitbit, 'make_request')
        self.make_request = fitbit_patch.start()
        self.addCleanup(fitbit_patch.stop)

    def testUpdatesSteps(self):
        self.make_request.return_value = {'activities-steps-intraday': { 'dataset': [
            {
                'time': '10:10:00',
                'value': 5
            }, {
                'time': '13:15:00',
                'value': 5
            }, {
                'time': '13:16:00',
                'value': 0
            }
        ]}}
        service = FitbitDayService(
            account = self.account,
            date = date(2018,2,14)
        )

        step_count = service.update_steps()

        self.assertEqual(step_count, 10)
        self.make_request.assert_called_with('https://api.fitbit.com/1/user/-/activities/steps/date/2018-02-14/1d/1min.json')
        self.assertEqual(FitbitMinuteStepCount.objects.count(), 2)

        self.make_request.return_value = {'activities-steps-intraday': { 'dataset': [
            {
                'time': '10:10:00',
                'value': 15
            }
        ]}}

        step_count = service.update_steps()
        self.assertEqual(step_count, 15)
        self.assertEqual(FitbitMinuteStepCount.objects.count(), 1)

    def testUpdateOnlySingleAccount(self):
        self.make_request.return_value = {'activities-steps-intraday': { 'dataset': [
            {
                'time': '10:10:00',
                'value': 15
            }
        ]}}

        other_account = FitbitAccount.objects.create(fitbit_user="other_user")
        FitbitMinuteStepCount.objects.create(
            account = other_account,
            steps = 150,
            time = datetime(2018,2,14,12,12).astimezone(pytz.UTC)
        )

        service = FitbitDayService(
            account = self.account,
            date = date(2018,2,14)
        )

        step_count = service.update_steps()

        self.assertEqual(step_count, 15)
        self.assertEqual(FitbitMinuteStepCount.objects.count(), 2)


class FitbitUpdatesHeartRate(TestBase):

    @patch.object(Fitbit, 'make_request')
    def test_process_heart_rate(self, make_request):
        make_request.return_value = { 'activities-heart-intraday': { 'dataset': [
            {
                'time': '10:00:00',
                'value': 77
            },
            {
                'time': '10:01:00',
                'value': 60
            },
            {
                'time': '11:00:00',
                'value': 100
            }
        ]}}
        service = FitbitDayService(
            account = self.account,
            date = date.today()
        )

        service.update_heart_rate()

        self.assertEqual(FitbitMinuteHeartRate.objects.count(), 3)

    @patch.object(Fitbit, 'make_request')
    def test_updates_single_account(self, make_request):
        make_request.return_value = { 'activities-heart-intraday': { 'dataset': [
            {
                'time': '10:00:00',
                'value': 77
            }
        ]}}
        other_account = FitbitAccount.objects.create(fitbit_user="other_user")
        FitbitMinuteHeartRate.objects.create(
            account = other_account,
            time = datetime.now().astimezone(pytz.UTC),
            heart_rate = 20
        )
        FitbitMinuteHeartRate.objects.create(
            account = self.account,
            time = datetime.now().astimezone(pytz.UTC),
            heart_rate = 88
        )
        service = FitbitDayService(
            account = self.account,
            date = date.today()
        )

        service.update_heart_rate()

        self.assertEqual(FitbitMinuteHeartRate.objects.count(), 2)
        # There should only be one of these
        heart_rate = FitbitMinuteHeartRate.objects.get(account=self.account)
        self.assertEqual(heart_rate.heart_rate, 77)

class FitbitUpdatesDistance(TestBase):

    @patch.object(Fitbit, 'make_request')
    def testUpdatesDistance(self, make_request):
        make_request.return_value = { 'activities-distance-intraday': { 'dataset': [
            {
                'time': '10:00:00',
                'value': '0.57'
            }, {
                'time': '11:00:00',
                'value': '0.33'
            }
        ]}}
        service = FitbitDayService(
            account = self.account,
            date = date(2018,2,14)
        )

        distance = service.update_distance()

        self.assertEqual(float(distance), 0.9)
        make_request.assert_called_with('https://api.fitbit.com/1/user/-/activities/distance/date/2018-02-14/1d/1min.json')


class FitbitActivityUpdates(TestBase):

    @patch.object(Fitbit, 'make_request')
    def testUpdateActivitiesOnDay(self, make_request):
        make_request.return_value = {
            'activities': [
                {
                    'logId': 123,
                    'startTime': '2018-02-14T07:07:00.000-7:00',
                    'duration': 1200000,
                    'averageHeartRate': 94,
                    'activityTypeId': 123456,
                    'activityName': 'Foo Ball'
                }
            ],
            'pagination': {
                'next': ''
            }
            }
        service = FitbitDayService(
            account = self.account,
            date = date(2018,2,14)
        )

        service.update_activities()

        make_request.assert_called_with('https://api.fitbit.com/1/user/-/activities/list.json?afterDate=2018-02-14&offset=0&limit=20&sort=asc')
        activity = FitbitActivity.objects.get()
        self.assertEqual(activity.fitbit_id, '123')
        self.assertEqual(activity.type.name, 'Foo Ball')
        self.assertEqual(activity.average_heart_rate, 94)
        self.assertEqual(activity.end_time, datetime(2018, 2, 14, 14, 27, tzinfo=pytz.UTC))

class UpdateFitbitDay(TestBase):

    def setUp(self):
        super().setUp()

        patcher = patch.object(update_fitbit_data, 'apply_async')
        self.update_fitbit_data = patcher.start()
        self.addCleanup(patcher.stop)        

    def test_queues_update_task(self):
        fitbit_update_date.send(
            sender = FitbitAccount,
            fitbit_user = self.account.fitbit_user,
            date = '2019-02-22'
        )

        self.update_fitbit_data.assert_called_with(kwargs={
            'fitbit_user': 'test',
            'date_string': '2019-02-22'
        })
