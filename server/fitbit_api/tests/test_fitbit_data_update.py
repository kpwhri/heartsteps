from unittest.mock import patch
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from fitbit import Fitbit

from fitbit_api.models import FitbitAccount, FitbitDay, FitbitMinuteStepCount
from fitbit_api.services import FitbitClient
from fitbit_api.tasks import update_fitbit_data

class GetUpdatedAcitivities(TestCase):

    @patch.object(FitbitClient, 'update_activities')
    @patch.object(FitbitClient, 'update_steps')
    def test_pull_account_data(self, update_steps, update_activities):
        account = FitbitAccount.objects.create(
            user = User.objects.create(username="test"),
            fitbit_user = "test"
        )

        update_fitbit_data(username="test", date_string="2018-02-14")

        fitbit_day = FitbitDay.objects.get(account=account)
        self.assertEqual(fitbit_day.format_date(), "2018-02-14")
        update_steps.assert_called()
        update_activities.assert_called()

    @patch.object(Fitbit, 'intraday_time_series')
    def test_gets_total_steps_for_day(self, intraday_time_series):
        intraday_time_series.return_value = {'activities-steps':[
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
        ]}
        account = FitbitAccount.objects.create(
            user = User.objects.create(username="test"),
            fitbit_user = "test"
        )
        day = FitbitDay(
            account = account,
            date = datetime(2018,2,14)
        )
        service = FitbitClient(account.user)

        service.update_steps(day)

        intraday_time_series.assert_called_with('activities/steps', base_date="2018-02-14")
        day = FitbitDay.objects.get()
        self.assertEqual(day.total_steps, 10)
        self.assertEqual(FitbitMinuteStepCount.objects.count(), 2)

    @patch.object(Fitbit, 'make_request')
    def test_gets_activities_for_day(self, make_request):
        account = FitbitAccount.objects.create(
            user = User.objects.create(username="test"),
            fitbit_user = "test"
        )
        day = FitbitDay(
            account = account,
            date = datetime(2018,2,14)
        )
        service = FitbitClient(account.user)

        service.update_activities(day)

        make_request.assert_called_with('https://api.fitbit.com/1/user/test/activities/list.json?afterDate=2018-02-13&offset=0&limit=20&sort=asc')

