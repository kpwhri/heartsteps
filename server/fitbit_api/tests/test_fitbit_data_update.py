import pytz
from unittest.mock import patch
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from fitbit import Fitbit

from fitbit_api.models import FitbitAccount, FitbitAccountUser, FitbitDay, FitbitMinuteStepCount, FitbitActivity
from fitbit_api.services import FitbitClient
from fitbit_api.tasks import update_fitbit_data

class GetUpdatedAcitivities(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.account = FitbitAccount.objects.create(
            fitbit_user = "test"
        )
        FitbitAccountUser.objects.create(
            user = self.user,
            account = self.account
        )

    @patch.object(FitbitClient, 'update_heart_rate')
    @patch.object(FitbitClient, 'update_activities')
    @patch.object(FitbitClient, 'update_steps')
    @patch.object(FitbitClient, 'get_timezone', return_value=pytz.timezone("Poland"))
    def test_pull_account_data(self, get_timezone, update_steps, update_activities, update_heart_rate):
        update_fitbit_data(username="test", date_string="2018-02-14")

        fitbit_day = FitbitDay.objects.get(account=self.account)
        self.assertEqual(fitbit_day.get_timezone().zone, "Poland")
        self.assertEqual(fitbit_day.format_date(), "2018-02-14")
        update_steps.assert_called()
        update_activities.assert_called()
        update_heart_rate.assert_called()

    @patch.object(Fitbit, 'intraday_time_series')
    def test_gets_total_steps_for_day(self, intraday_time_series):
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
        day = FitbitDay.objects.create(
            account = self.account,
            date = datetime(2018,2,14),
            timezone = "UTC"
        )
        service = FitbitClient(self.user)

        service.update_steps(day)

        day = FitbitDay.objects.get()
        day.update_steps()

        intraday_time_series.assert_called_with('activities/steps', base_date="2018-02-14")
        self.assertEqual(day.step_count, 10)
        self.assertEqual(FitbitMinuteStepCount.objects.count(), 2)

    @patch.object(Fitbit, 'make_request')
    def test_gets_activities_for_day(self, make_request):
        make_request.return_value = {
            'activities': [
                {
                    'logId': 123,
                    'startTime': '2018-02-14T07:07:00.000-7:00',
                    'duration': 1200000,
                    'activityLevel': [{
                        'name': 'sedentary',
                        'minutes': 15
                    }, {
                        'name': 'very',
                        'minutes': 5
                    }],
                    'activityTypeId': 123456,
                    'activityName': 'Foo Ball'
                }
            ],
            'pagination': {
                'next': ''
            }
            }
        day = FitbitDay.objects.create(
            account = self.account,
            date = datetime(2018,2,14)
        )
        service = FitbitClient(self.user)

        service.update_activities(day)

        make_request.assert_called_with('https://api.fitbit.com/1/user/test/activities/list.json?afterDate=2018-02-14&offset=0&limit=20&sort=asc')
        activity = FitbitActivity.objects.get()
        self.assertEqual(activity.fitbit_id, '123')
        self.assertEqual(activity.end_time, datetime(2018, 2, 14, 14, 27, tzinfo=pytz.UTC))
        self.assertEqual(activity.vigorous_minutes, 5)
        self.assertEqual(activity.moderate_minutes, 15)
