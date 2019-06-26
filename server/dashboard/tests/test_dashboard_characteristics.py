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
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create(username='test')
        self.participant = Participant.objects.create(
            user=self.user,
            enrollment_token='test',
            heartsteps_id='test'
        )
        self.fitbit_account = FitbitAccount.objects.create(
            uuid='test',
            fitbit_user='test'
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
        AuthenticationSession.objects.create(
            token='test',
            state='test',
            user=self.user
        )
        self.assertEqual(self.participant.fitbit_authorized, True)

    def test_fitbit_authorized_false(self):
        AuthenticationSession.objects.all().delete()
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
        self.assertEqual(self.participant.last_fitbit_sync(),
                         pytz.utc.localize(self.basetime))

    def test_last_fitbit_sync_has_not_synched(self):
        self.assertEqual(self.participant.last_fitbit_sync(), 0)

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

    def test_adherence_no_fitbit_data_no_data(self):
        self.assertEqual(self.participant.adherence_no_fitbit_data, 0)

    def make_subscription_hours_ago(self, hrs):
        hours_ago = timedelta(hours=hrs)
        last_sync = pytz.utc.localize(datetime.now() - hours_ago)
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
                                                created=last_sync)

    def test_adherence_no_fitbit_data_no_data_48hrs(self):
        self.make_subscription_hours_ago(49)
        self.assertEqual(self.participant.adherence_no_fitbit_data, 48)

    def test_adherence_no_fitbit_data_no_data_72hrs(self):
        self.make_subscription_hours_ago(73)
        self.assertEqual(self.participant.adherence_no_fitbit_data, 72)

    def test_adherence_no_fitbit_data_no_data_week(self):
        self.make_subscription_hours_ago((24*7) + 1)
        self.assertEqual(self.participant.adherence_no_fitbit_data, 24*7)

    def test_adherence_no_fitbit_data_recent_sync(self):
        self.make_subscription_hours_ago(23)
        self.assertEqual(self.participant.adherence_no_fitbit_data, 0)

    def test_adherence_app_use_not_used(self):
        self.assertEqual(self.participant.adherence_app_use(), 0)

    def test_adherence_app_use_used_recent(self):
        self.make_page_view(datetime.now())
        self.assertEqual(self.participant.adherence_app_use(), 0)

    def test_adherence_app_use_used_96_hours(self):
        hours_ago = timedelta(hours=97)
        last_page_view = datetime.now() - hours_ago
        self.make_page_view(last_page_view)
        self.assertEqual(self.participant.adherence_app_use(), 96)

    def test_adherence_app_use_used_week(self):
        hours_ago = timedelta(hours=(24*7)+1)
        last_page_view = datetime.now() - hours_ago
        self.make_page_view(last_page_view)
        self.assertEqual(self.participant.adherence_app_use(), 24*7)

    def test_enrollment_date_no_enrollment(self):
        participant = Participant.objects.create(
            enrollment_token='enrolldt1',
            heartsteps_id='enrolldt1'
        )
        self.assertEqual(participant.enrollment_date(), None)

    def test_enrollment_date_enrolled(self):
        participant = Participant.objects.create(
            user=self.user,
            enrollment_token='1234-5678',
            heartsteps_id='000000'
        )
        self.assertEqual(participant.enrollment_date(), self.user.date_joined)
