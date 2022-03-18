import pytz
from datetime import date, datetime, timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase

from fitbit_activities.models import FitbitDay
from fitbit_api.models import FitbitAccount, FitbitAccountUser, \
    FitbitSubscription, FitbitSubscriptionUpdate
from fitbit_authorize.models import AuthenticationSession
from page_views.models import PageView
from participants.models import Participant
from watch_app.models import StepCount, WatchInstall


class DashboardParticipantTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.participant = Participant.objects.create(
            user=self.user,
            enrollment_token='test',
            heartsteps_id='test'
        )
        self.fitbit_account = FitbitAccount.objects.create(
            fitbit_user='test',
            access_token = 'test',
            refresh_token = 'test',
            expires_at = datetime.now().timestamp()
        )
        self.fitbit_account_user, _ = FitbitAccountUser.create_or_update(
            user=self.user,
            account=self.fitbit_account
        )
        self.basetime = datetime(2019, 1, 1, 12, 12, 12)
