import pytz
from unittest.mock import patch
from datetime import datetime, date

from django.test import TestCase
from django.contrib.auth.models import User

from fitbit import Fitbit

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitDay, FitbitMinuteStepCount, FitbitActivity
from fitbit_api.services import FitbitClient, FitbitDayService
from fitbit_api.tasks import update_fitbit_data

class TestBase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
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

    @patch.object(FitbitDayService, 'update_heart_rate', return_value=50)
    @patch.object(FitbitDayService, 'update_activities')
    @patch.object(FitbitDayService, 'update_steps', return_value=20)
    @patch.object(FitbitDayService, 'update_distance', return_value=0.123)
    def testUpdateTaskCreatesDay(self, update_distance, update_steps, update_activities, update_heart_rate):
        self.timezone.return_value = pytz.timezone('Poland')

        update_fitbit_data(username=self.account.fitbit_user, date_string="2018-02-14")

        fitbit_day = FitbitDay.objects.get(account=self.account)
        self.assertEqual(fitbit_day.get_timezone().zone, "Poland")
        self.assertEqual(fitbit_day.date.strftime('%Y-%m-%d'), "2018-02-14")
        self.assertEqual(fitbit_day.step_count, 20)
        self.assertEqual(fitbit_day.distance, 0.123)
        self.assertEqual(fitbit_day.average_heart_rate, 50)

        update_steps.assert_called()
        update_distance.assert_called()
        update_activities.assert_called()
        update_heart_rate.assert_called()

class FitbitStepUpdates(TestBase):

    @patch.object(Fitbit, 'intraday_time_series')
    def testUpdatesSteps(self, intraday_time_series):
        intraday_time_series.return_value = {'activities-steps-intraday': { 'dataset': [
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
        intraday_time_series.assert_called_with('activities/steps', base_date="2018-02-14")
        self.assertEqual(FitbitMinuteStepCount.objects.count(), 2)

        intraday_time_series.return_value = {'activities-steps-intraday': { 'dataset': [
            {
                'time': '10:10:00',
                'value': 15
            }
        ]}}

        step_count = service.update_steps()
        self.assertEqual(step_count, 15)
        self.assertEqual(FitbitMinuteStepCount.objects.count(), 1)

class FitbitUpdatesDistance(TestBase):

    @patch.object(Fitbit, 'intraday_time_series')
    def testUpdatesDistance(self, intraday_time_series):
        intraday_time_series.return_value = { 'activities-distance-intraday': { 'dataset': [
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
        intraday_time_series.assert_called()


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

        make_request.assert_called_with('https://api.fitbit.com/1/user/test/activities/list.json?afterDate=2018-02-14&offset=0&limit=20&sort=asc')
        activity = FitbitActivity.objects.get()
        self.assertEqual(activity.fitbit_id, '123')
        self.assertEqual(activity.type.name, 'Foo Ball')
        self.assertEqual(activity.average_heart_rate, 94)
        self.assertEqual(activity.end_time, datetime(2018, 2, 14, 14, 27, tzinfo=pytz.UTC))
