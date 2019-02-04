from datetime import timedelta, datetime
from dateutil import parser as dateutil_parser
import pytz

from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit

from fitbit_api.models import User, FitbitAccount, FitbitAccountUser, FitbitSubscription, FitbitDay, FitbitActivity, FitbitActivityType, FitbitMinuteStepCount, FitbitDailyUnprocessedData

class FitbitService:

    class NoAccount(ImproperlyConfigured):
        pass

    def __init__(self, account=None, user=None, username=None):
        if username:
            user = User.objects.get(username=username)
        if user:
            account = FitbitService.get_account(user)
        if not account:
            raise FitbitService.NoAccount()
        self.__account = account
        self.account = account
        self.__user = user

    def get_users(self):
        users = []
        for account_user in FitbitAccountUser.objects.filter(account=self.__account).all():
            users.append(account_user.user)
        return users

    def get_account(user):
        try:
            account_user = FitbitAccountUser.objects.get(user=user)
            return account_user.account
        except FitbitAccountUser.DoesNotExist:
            raise FitbitService.NoAccount()

    def create_account(user, fitbit_username=None):
        if not fitbit_username:
            fitbit_username = user.username
        account, created = FitbitAccount.objects.get_or_create(
            fitbit_user = fitbit_username
        )
        account_user, created = FitbitAccountUser.objects.update_or_create(
            user = user,
            defaults = {
                'account': account
            }
        )
        return account


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

    def __init__(self, user=None, account=None):
        if account:
            self.account = account
        elif user:
            try:
                user_account = FitbitAccountUser.objects.get(user=user)
                self.account = user_account.account
            except FitbitAccountUser.DoesNotExist:
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
        subscriptions = FitbitSubscription.objects.filter(fitbit_account = self.account).all()
        if len(subscriptions) > 0:
            return True
        else:
            return False

    def subscriptions_update(self):
        existing_subscription_ids = []
        for subscription in FitbitSubscription.objects.filter(fitbit_account = self.account).all():
            existing_subscription_ids.append(subscription.uuid)
        fitbit_subscription_ids = self.list_subscriptions()
        for subscription_id in fitbit_subscription_ids:
            if not subscription_id in existing_subscription_ids:
                FitbitSubscription.objects.create(
                    uuid = subscription_id,
                    fitbit_account = self.account
                )
        for existing_id in existing_subscription_ids:
            if existing_id not in fitbit_subscription_ids:
                FitbitSubscription.objects.filter(uuid=existing_id).delete()
        return False

    def list_subscriptions(self):
        subscription_ids = []
        response = self.client.list_subscriptions()
        if 'apiSubscriptions' in response:
            for subscription in response['apiSubscriptions']:
                subscription_ids.append(subscription['subscriptionId'])
        return subscription_ids

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

    def get_timezone(self):
        if hasattr(self, '__timezone'):
            return self.__timezone
        response = self.client.user_profile_get()
        timezone = response['user']['timezone']
        self.__timezone = pytz.timezone(timezone)
        return self.__timezone

    def get_day(self, date_string):
        date = datetime.strptime(date_string, '%Y-%m-%d')
        try:
            day = FitbitDay.objects.get(
                account = self.account,
                date = date
            )
        except FitbitDay.DoesNotExist:
            timezone = self.get_timezone()
            day = FitbitDay.objects.create(
                account = self.account,
                date = date,
                timezone = timezone.zone
            )
        return day

    def update_heart_rate(self, fitbit_day):
        url = "{0}/{1}/user/{user_id}/activities/heart/date/{date}/1d/1min.json".format(
            *self.client._get_common_args(),
            user_id = self.account.fitbit_user,
            date = fitbit_day.format_date()
        )
        response = self.client.make_request(url)
        timezone = fitbit_day.get_timezone()
        FitbitDailyUnprocessedData.objects.update_or_create(account=self.account, day=fitbit_day, defaults={
            'category': 'heart rate',
            'payload': response,
            'timezone': timezone.zone
        })

    def request_activities(self, fitbit_day):
        url = "{0}/{1}/user/{user_id}/activities/list.json?afterDate={after_date}&offset=0&limit=20&sort=asc".format(
            *self.client._get_common_args(),
            user_id = self.account.fitbit_user,
            after_date = fitbit_day.format_date()
        )
        response = self.client.make_request(url)
        return response

    def update_activities(self, fitbit_day, request_url=None):
        if request_url:
            response = self.client.make_request(request_url)
        else:   
            response = self.request_activities(fitbit_day)
        activities = response['activities']
        for activity in activities:
            startTime = dateutil_parser.parse(activity['startTime'])
            if startTime.strftime('%Y-%m-%d') == fitbit_day.format_date():
                self.save_activity(activity, fitbit_day)
        if len(activities) > 0:
            lastActivityStartTime = dateutil_parser.parse(activities[-1]['startTime'])
            if lastActivityStartTime.strftime('%Y-%m-%d') == fitbit_day.format_date():
                if response['pagination']['next'] is not '':
                    self.update_activities(fitbit_day, request_url=response['pagination']['next'])

    def save_activity(self, activity, fitbit_day):
        start_time = dateutil_parser.parse(activity['startTime'])
        end_time = start_time + timedelta(milliseconds=activity['duration'])
        average_heart_rate = activity['averageHeartRate']

        activity_type, _ = FitbitActivityType.objects.get_or_create(
            fitbit_id = activity['activityTypeId'],
            name = activity['activityName']
        )

        FitbitActivity.objects.update_or_create(
            fitbit_id = activity['logId'], defaults={
                'account': self.account,
                'type': activity_type,
                'day': fitbit_day,
                'average_heart_rate': average_heart_rate,
                'start_time': start_time,
                'end_time': end_time,
                'payload': activity
            }
        )

    def update_steps(self, fitbit_day):
        response = self.client.intraday_time_series('activities/steps', base_date=fitbit_day.format_date())
        
        timezone = fitbit_day.get_timezone()
        FitbitDailyUnprocessedData.objects.update_or_create(account=self.account, day=fitbit_day, defaults={
            'category': 'steps',
            'payload': response,
            'timezone': timezone.zone
        })
        FitbitMinuteStepCount.objects.filter(account=self.account, day=fitbit_day).delete()
        
        for stepInterval in response['activities-steps-intraday']['dataset']:
            if stepInterval['value'] > 0:
                step_datetime = datetime.strptime(
                        "%s %s" % (fitbit_day.format_date(), stepInterval['time']),
                        "%Y-%m-%d %H:%M:%S"
                    )
                step_datetime = timezone.localize(step_datetime)
                step_datetime_utc = step_datetime.astimezone(pytz.utc)

                FitbitMinuteStepCount.objects.create(
                    account = self.account,
                    day = fitbit_day,
                    time = step_datetime_utc,
                    steps = stepInterval['value']
                )

class FitbitDayService(FitbitService):

    def __init__(self, date, account=None, user=None, username=None):
        super().__init__(account, user, username)
        self.__client = FitbitClient(
            account = self.account
        )
        self.__day = self.__client.get_day(
            date_string = FitbitDayService.date_to_string(date)
        )

    def date_to_string(date):
        return date.strftime('%Y-%m-%d')
    
    def string_to_date(string):
        return datetime.strptime(string, '%Y-%m-%d')

    def update(self):
        self.__client.update_steps(self.__day)
        self.__client.update_activities(self.__day)
        self.__client.update_heart_rate(self.__day)
        self.__day.update()
