from datetime import timedelta, datetime
from dateutil import parser as dateutil_parser
from decimal import Decimal
import pytz

from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit
from fitbit.exceptions import HTTPUnauthorized

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

    @property
    def fitbit_user(self):
        return self.account.fitbit_user

    def is_authorized(self):
        if self.account.access_token:
            return True
        else:
            return False


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

def format_fitbit_date(date):
    return date.strftime('%Y-%m-%d')

def parse_fitbit_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d')

class FitbitClient():

    class ClientError(RuntimeError):
        pass

    class Unauthorized(ClientError):
        pass

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

    def make_request(self, url):
        formatted_url = '{0}/{1}/{url}'.format(
            *self.client._get_common_args(),
            url = url
        )
        try:
            return self.client.make_request(formatted_url)
        except HTTPUnauthorized:
            raise FitbitClient.Unauthorized('Fitbit unauthorized')
        except Exception as e:
            raise FitbitClient.ClientError('Unknown error')

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

    def get_heart_rate(self, date):
        url = "user/-/activities/heart/date/{date}/1d/1min.json".format(
            *self.client._get_common_args(),
            date = format_fitbit_date(date)
        )
        response = self.make_request(url)
        return response['activities-heart-intraday']['dataset']

    def __request_activities(self, date):
        url = "user/-/activities/list.json?afterDate={after_date}&offset=0&limit=20&sort=asc".format(
            after_date = format_fitbit_date(date)
        )
        response = self.make_request(url)
        return response

    def get_activities(self, date, request_url=None, activities=[]):
        if request_url:
            response = self.client.make_request(request_url)
        else:   
            response = self.__request_activities(date)
        
        more_activities = True
        for activity in response['activities']:
            startTime = dateutil_parser.parse(activity['startTime'])
            if startTime.strftime('%Y-%m-%d') == date.strftime('%Y-%m-%d'):
                activities.append(activity)
            else:
                more_activities = False
        if more_activities and response['pagination']['next'] is not '':
            return self.get_activities(
                date = date,
                request_url=response['pagination']['next'],
                activities = activities    
            )
        else:
            return activities

    def format_date(self, date):
        return format_fitbit_date(date)
    
    def parse_date(self, date):
        return parse_fitbit_date(date)
        
    def get_intraday_activity(self, activity_type, date):
        response = self.make_request('user/-/activities/{activity_type}/date/{date}/1d/1min.json'.format(
            activity_type = activity_type,
            date = self.format_date(date)
        ))
        return response['activities-%s-intraday' % activity_type]['dataset']

class FitbitDayService(FitbitService):

    def __init__(self, date=None, account=None, user=None, username=None, fitbit_day=None):
        if fitbit_day:
            account = fitbit_day.account
        super().__init__(account, user, username)
        self.__client = FitbitClient(
            account = self.account
        )
        if not fitbit_day and not date:
            raise ImproperlyConfigured('No date supplied')
        if date:
            fitbit_day = self.__get_fitbit_day(date)
        self.day = fitbit_day
        self.date = fitbit_day.date

    def __get_fitbit_day(self, date):
        try:
            return FitbitDay.objects.get(
                account = self.account,
                date = date
            )
        except FitbitDay.DoesNotExist:
            timezone = self.__client.get_timezone()
            return FitbitDay.objects.create(
                account = self.account,
                date = date,
                _timezone = timezone.zone
            )

    def update(self):
        self.day.step_count = self.update_steps()
        self.day._distance = self.update_distance()
        self.update_heart_rate() 
        self.update_activities()
        
        self.day.save()

    def update_activities(self):
        for activity in self.__client.get_activities(self.date):
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
                    'day': self.day,
                    'average_heart_rate': average_heart_rate,
                    'start_time': start_time,
                    'end_time': end_time,
                    'payload': activity
                }
            )

    def update_heart_rate(self):
        data = self.__client.get_heart_rate(self.date)
        timezone = self.day.get_timezone()
        FitbitDailyUnprocessedData.objects.update_or_create(
            account=self.account,
            day=self.day,
            category = 'heart rate',
            defaults={
                'payload': data,
                'timezone': timezone.zone
            }
        )
        return data

    def _get_intraday_time_series(self, activity_type):
        timezone = self.day.get_timezone()
        data = self.__client.get_intraday_activity(activity_type, self.date)
        FitbitDailyUnprocessedData.objects.update_or_create(
            account=self.account,
            day=self.day,
            category = activity_type,
            defaults={
                'payload': data,
                'timezone': timezone.zone
            }
        )

        processed_data = []
        for interval in data:
            interval_datetime = datetime.strptime(
                    "%s %s" % (
                        format_fitbit_date(self.date),
                        interval['time']
                    ),
                    "%Y-%m-%d %H:%M:%S"
                )
            interval_datetime = timezone.localize(interval_datetime)
            processed_data.append({
                'datetime': interval_datetime.astimezone(pytz.utc),
                'value': interval['value']
            })
        return processed_data

    def update_steps(self):
        step_intervals = []
        total_steps = 0
        for interval in self._get_intraday_time_series('steps'):
            if interval['value'] > 0:
                total_steps += interval['value']
                step_intervals.append(FitbitMinuteStepCount(
                    account = self.account,
                    time = interval['datetime'],
                    steps = interval['value']
                ))
        
        FitbitMinuteStepCount.objects.filter(
            time__range = [self.day.get_start_datetime(), self.day.get_end_datetime()]
        ).delete()

        FitbitMinuteStepCount.objects.bulk_create(step_intervals)
        return total_steps

    def update_distance(self):
        total_distance = Decimal(0)
        for interval in self._get_intraday_time_series('distance'):
            total_distance += Decimal(interval['value'])
        return total_distance
