import pytz
from datetime import date, datetime, timedelta

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
        self.fitbit_account_user = FitbitAccountUser.objects.create(
            user=self.user,
            account=self.fitbit_account
        )
        self.basetime = datetime(2019, 1, 1, 12, 12, 12)

    def test_wore_fitbit_days_user_exists(self):
        FitbitDay.objects.bulk_create([
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 19), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 20), step_count=10000,
                      wore_fitbit=False)
        ])
        self.assertEqual(self.participant.wore_fitbit_days, 1)

    def test_watch_app_installed_true(self):
        WatchInstall.objects.create(
            user=self.user,
            version='test'
        )
        self.assertEqual(self.participant.watch_app_installed(), True)

    def test_watch_app_installed_false(self):
        WatchInstall.objects.all().delete()
        self.assertEqual(self.participant.watch_app_installed(), False)

    def test_fitbit_authorized_true(self):
        self.assertEqual(self.participant.fitbit_authorized, True)

    def test_fitbit_authorized_false(self):
        self.fitbit_account.access_token = None
        self.fitbit_account.save()
        self.assertEqual(self.participant.fitbit_authorized, False)

    def test_last_fitbit_sync_has_synched(self):
        subscription = FitbitSubscription.objects.create(
            fitbit_account=self.fitbit_account,
            uuid='test'
        )
        FitbitSubscriptionUpdate.objects.create(
            subscription=subscription,
            uuid='test',
            payload="['test':'test']"
        )
        FitbitSubscriptionUpdate.objects.filter(uuid='test').update(
                                 created=pytz.utc.localize(self.basetime))
        self.assertEqual(self.participant.fitbit_last_updated,
                         pytz.utc.localize(self.basetime))

    def test_last_fitbit_sync_has_not_synched(self):
        self.assertEqual(self.participant.fitbit_last_updated, None)

    def make_page_view(self, dtm):
        PageView.objects.create(
            user=self.user,
            uri='https://test.com',
            time=pytz.utc.localize(dtm)
        )

    def test_last_page_view_has_viewed(self):
        self.make_page_view(self.basetime)
        self.assertEqual(self.participant.last_page_view(),
                         pytz.utc.localize(self.basetime))

    def test_last_page_view_has_not_viewed(self):
        self.assertEqual(self.participant.last_page_view(), None)

    def test_last_watch_app_data_has_not_used(self):
        self.assertEqual(self.participant.last_watch_app_data(), None)

    def test_last_watch_app_data_used(self):
        end_dtm = pytz.utc.localize(self.basetime) + timedelta(seconds=60)
        StepCount.objects.create(
            user=self.user,
            steps=100,
            start=pytz.utc.localize(self.basetime),
            end=end_dtm
        )
        self.assertEqual(self.participant.last_watch_app_data(), end_dtm)

    def test_adherence_install_app_not_due(self):
        FitbitDay.objects.bulk_create([
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 19), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 20), step_count=10000,
                      wore_fitbit=True)
        ])
        self.assertEqual(self.participant.adherence_install_app(), False)

    def test_adherence_install_app_due(self):
        FitbitDay.objects.bulk_create([
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 19), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 20), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 21), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 22), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 23), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 24), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 25), step_count=10000,
                      wore_fitbit=True)
        ])
        self.assertEqual(self.participant.adherence_install_app(), True)

    def test_adherence_install_app_already_using(self):
        self.make_page_view(self.basetime)
        FitbitDay.objects.bulk_create([
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 19), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 20), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 21), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 22), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 23), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 24), step_count=10000,
                      wore_fitbit=True),
            FitbitDay(account=self.fitbit_account,
                      date=date(2019, 6, 25), step_count=10000,
                      wore_fitbit=True)
        ])
        self.assertEqual(self.participant.adherence_install_app(), False)

    def test_enrollment_date_no_enrollment(self):
        participant = Participant.objects.create(
            enrollment_token='enrolldt1',
            heartsteps_id='enrolldt1'
        )
        self.assertEqual(participant.date_joined, None)

    def test_enrollment_date_enrolled(self):
        participant = Participant.objects.create(
            user=self.user,
            enrollment_token='1234-5678',
            heartsteps_id='000000'
        )
        self.assertEqual(participant.date_joined, self.user.date_joined)
