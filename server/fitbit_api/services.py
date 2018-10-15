from datetime import timedelta, datetime

from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit

from fitbit_api.models import FitbitAccount, FitbitSubscription, FitbitDay, FitbitActivity, FitbitMinuteStepCount

def create_fitbit(**kwargs):
    consumer_key = None
    consumer_secret = None
    try:
        consumer_key = settings.FITBIT_CONSUMER_KEY
        consumer_secret = settings.FITBIT_CONSUMER_SECRET
    except:
        raise ImproperlyConfigured('Missing Fitbit API credentials')
    return Fitbit(consumer_key, consumer_secret, **kwargs)

def create_callback_url(request):
    complete_url = request.build_absolute_uri(reverse('fitbit-authorize-process'))
    if 'https://' not in complete_url:
        complete_url = complete_url.replace('http://', 'https://')

class FitbitClient():

    def __init__(self, user):
        try:
            self.account = FitbitAccount.objects.get(user=user)
        except FitbitAccount.DoesNotExist:
            raise ValueError("Fitbit Account doesn't exist")
        self.client = self.create_client()


    def create_client(self):
        return create_fitbit(**{
            'access_token': self.account.access_token,
            'refresh_token': self.account.refresh_token,
            'expires_at': self.account.expires_at,
            'refresh_cb': lambda token: self.update_token(token)
        })

    def update_token(self, token):
        self.account.access_token = token['access_token']
        self.account.refresh_token = token['refresh_token']
        self.account.expires_at = token['expires_at']
        self.account.save()

    def is_subscribed(self):
        response = self.client.list_subscriptions()
        if 'apiSubscriptions' in response:
            for subscription in response['apiSubscriptions']:
                if subscription['subscriptionId'] == str(self.subscription.uuid):
                    return True
        return False

    def subscribe(self):
        if not hasattr(settings, 'FITBIT_SUBSCRIBER_ID'):
            raise ImproperlyConfigured('No FitBit Subscriber ID')
        try:
            self.subscription = FitbitSubscription.objects.get(fitbit_account=self.account)
        except FitbitSubscription.DoesNotExist:
            self.subscription = FitbitSubscription.objects.create(
                fitbit_account = self.account
            )
        try:
            self.client.subscription(
                subscription_id = str(self.subscription.uuid),
                subscriber_id = settings.FITBIT_SUBSCRIBER_ID
            )
            return True
        except:
            return False

    def verify_subscription_code(code):
        if not hasattr(settings, 'FITBIT_SUBSCRIBER_VERIFICATION_CODE'):
            raise ImproperlyConfigured('No FitBit Subscriber Verification Code')
        if code == settings.FITBIT_SUBSCRIBER_VERIFICATION_CODE:
            return True
        else:
            return False

    def get_day(self, date_string):
        date = datetime.strptime(date_string, '%Y-%m-%d')
        try:
            day = FitbitDay.objects.get(
                account = self.account,
                date = date
            )
        except FitbitDay.DoesNotExist:
            day = FitbitDay.objects.create(
                account = self.account,
                date = date
            )
        return day

    def update_activities(self, fitbit_day):
        previous_day = fitbit_day.date - timedelta(days=1)
        url = "{0}/{1}/user/{user_id}/activities/list.json?afterDate={after_date}&offset=0&limit=20&sort=asc".format(
            *self.client._get_common_args(),
            user_id = self.account.fitbit_user,
            after_date = self.client._get_date_string(previous_day)
        )

        activities = []
        response = self.client.make_request(url)
        for activity in response['activities']:
            activities.append(activity)
        return activities

    def update_steps(self, fitbit_day):
        response = self.client.intraday_time_series('activities/steps', base_date=fitbit_day.format_date())

        FitbitMinuteStepCount.objects.filter(account=self.account, day=fitbit_day).delete()
        
        total_steps = 0
        for stepInterval in response['activities-steps']:
            if stepInterval['value'] > 0:
                total_steps += stepInterval['value']
                FitbitMinuteStepCount.objects.create(
                    account = self.account,
                    day = fitbit_day,
                    time = datetime.strptime(
                        "%s %s" % (fitbit_day.format_date(), stepInterval['time']),
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    steps = stepInterval['value']
                )
        fitbit_day.total_steps = total_steps
        fitbit_day.save()

