from datetime import timedelta, datetime
from dateutil import parser as dateutil_parser
import pytz

# from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit
from fitbit.exceptions import HTTPTooManyRequests
from fitbit.exceptions import HTTPUnauthorized

from days.services import DayService
# from daily_step_goals.services import StepGoalsService
import daily_step_goals.services

from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from fitbit_api.models import FitbitSubscription
from fitbit_api.models import FitbitSubscriptionUpdate
from fitbit_api.models import User

import oauthlib

from fitbit_api.models import FitbitConsumerKey
from system_settings.models import SystemSetting

class FitbitService:

    class AccountNeverUpdated(RuntimeError):
        pass

    class NoAccount(ImproperlyConfigured):
        pass

    def __init__(self, account=None, user=None, username=None, fitbit_user=None):
        if username:
            user = User.objects.get(username=username)
        if user:
            account = FitbitService.get_account(user)
        if fitbit_user:
            try:
                account = FitbitAccount.objects.get(fitbit_user=fitbit_user)
            except FitbitAccount.DoesNotExist:
                raise FitbitService.NoAccount()
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

    def get_latest_step_goal(self):
        step_goal_service = daily_step_goals.services.StepGoalsService(user=self.__user)
        goal = step_goal_service.get_goal()

        return goal

    @property
    def fitbit_user(self):
        return self.account.fitbit_user

    def is_authorized(self):
        if self.account.access_token:
            return True
        else:
            return False

    def was_updated_on(self, date):
        day_service = DayService(user=self.__user)
        start = day_service.get_start_of_day(date)
        end = day_service.get_end_of_day(date)
        return self.account.was_updated_between(start, end)

    def first_updated_on(self):
        return self.__account.get_first_update()

    def last_updated_on(self):
        return self.__account.get_last_update()

    def remove_credentials(self):
        self.account.remove_credentials()


def create_fitbit(**kwargs):
    consumer_key = None
    consumer_secret = None
    try:
        fitbit_consumer_key_obj = FitbitConsumerKey.objects.order_by('-created').first()
        consumer_key = fitbit_consumer_key_obj.key
        consumer_secret = fitbit_consumer_key_obj.secret
        
        # consumer_key = settings.FITBIT_CONSUMER_KEY
        # consumer_secret = settings.FITBIT_CONSUMER_SECRET
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

    class TooManyRequests(ClientError):
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

    def make_request(self, url, data=None, method=None):
        formatted_url = '{0}/{1}/{url}'.format(
            *self.client._get_common_args(),
            url = url
        )
        try:
            return self.client.make_request(
                url = formatted_url,
                data = data,
                method = method
            )
        except HTTPUnauthorized:
            self.account.remove_credentials()
            raise FitbitClient.Unauthorized('Fitbit unauthorized')
        except HTTPTooManyRequests:
            raise FitbitClient.TooManyRequests('Too many requests')
        except Exception as e:
            raise FitbitClient.ClientError('Unknown error')

    def update_step_goals(self, steps):
        return self.client.activities_daily_goal(steps=steps)
        
    def is_subscribed(self):
        subscriptions = FitbitSubscription.objects.filter(fitbit_account = self.account).all()
        if len(subscriptions) > 0:
            return True
        else:
            return False

    # TODO: delete print debugging
    def subscriptions_update(self):
        existing_subscription_ids = []
        for subscription in FitbitSubscription.objects.filter(fitbit_account = self.account).all():
            existing_subscription_ids.append(subscription.uuid)
        fitbit_subscription_ids = self.list_subscriptions()
        print('existing subscription ids', existing_subscription_ids, flush=True)
        print('fitbit subscription ids: ', fitbit_subscription_ids)
        for subscription_id in fitbit_subscription_ids:
            if not subscription_id in existing_subscription_ids:
                print('creating subscription, id num: ', subscription_id)
                FitbitSubscription.objects.create(
                    uuid = subscription_id,
                    fitbit_account = self.account
                )
        for existing_id in existing_subscription_ids:
            if existing_id not in fitbit_subscription_ids:
                print('deleting subscription, id num: ', existing_id)
                FitbitSubscription.objects.filter(uuid=existing_id).delete()
        return False

    def list_subscriptions(self):
        subscription_ids = []
        response = self.client.list_subscriptions(collection='activities')
        if 'apiSubscriptions' in response:
            for subscription in response['apiSubscriptions']:
                subscription_ids.append(subscription['subscriptionId'])
        return subscription_ids

    # TODO: delete print debugging
    def subscribe(self):
        FITBIT_SUBSCRIBER_ID = SystemSetting.get('FITBIT_SUBSCRIBER_ID')
        if FITBIT_SUBSCRIBER_ID == "":
            print('ERROR: no fitbit subscriber ID')
            raise ImproperlyConfigured('No FitBit Subscriber ID')
        try:
            self.subscription = FitbitSubscription.objects.get(fitbit_account=self.account)
            print('found subscription: ', self.subscription)
        except FitbitSubscription.DoesNotExist:
            print('ERROR: FitbitSubscription.DoesNotExist')
            self.subscription = FitbitSubscription.objects.create(
                fitbit_account = self.account
            )
            print('created new FitbitSubscription object: ', self.subscription)

        try:
            # TODO: supposed to be self.subscription?
            self.client.subscription(
                subscription_id = str(self.subscription.uuid),
                subscriber_id = FITBIT_SUBSCRIBER_ID,
                collection='activities'
            )
            return True
        except:
            return False

    def unsubscribe(self):
        subscription_ids = self.list_subscriptions()
        for sid in subscription_ids:
            self.make_request(
                url = 'user/-/apiSubscriptions/%s.json' % (sid),
                method = 'DELETE'
            )

    def verify_subscription_code(code):
        FITBIT_SUBSCRIBER_VERIFICATION_CODE = SystemSetting.get('FITBIT_SUBSCRIBER_VERIFICATION_CODE')
        
        if FITBIT_SUBSCRIBER_VERIFICATION_CODE == "":
            raise ImproperlyConfigured('No FitBit Subscriber Verification Code')
        if code == FITBIT_SUBSCRIBER_VERIFICATION_CODE:
            return True
        else:
            return False

    def get_timezone(self):
        if hasattr(self, '__timezone'):
            return self.__timezone
        try:
            response = self.client.user_profile_get()
            timezone = response['user']['timezone']
            self.__timezone = pytz.timezone(timezone)
            return self.__timezone
        except (HTTPUnauthorized, oauthlib.oauth2.rfc6749.errors.InvalidGrantError) as e:
            from user_event_logs.models import EventLog
            import pprint
            EventLog.log(None, "server/fitbit_api/services.py:264/{}".format(pprint.pformat(e.__dict__)), EventLog.ERROR)
            raise FitbitClient.Unauthorized()

    def __request_activities(self, date):
        url = "user/-/activities/list.json?afterDate={after_date}&offset=0&limit=20&sort=asc".format(
            after_date = format_fitbit_date(date)
        )
        response = self.make_request(url)
        return response

    def get_activities(self, date, request_url=None, activities=None):
        if not activities:
            activities = []
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

    def format_datetime(self, dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')

    def parse_datetime(self, string):
        dt = datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f')
        return dt.replace(tzinfo = self.get_timezone())

    def get_intraday_activity(self, activity_type, date):
        response = self.make_request('user/-/activities/{activity_type}/date/{date}/1d/1min.json'.format(
            activity_type = activity_type,
            date = self.format_date(date)
        ))
        return response['activities-%s-intraday' % activity_type]['dataset']

    def get_steps(self, date):
        return self.get_intraday_activity(
            activity_type='steps',
            date = date
        )

    def get_distance(self, date):
        return self.get_intraday_activity(
            activity_type='distance',
            date = date
        )

    def get_heart_rate(self, date):
        url = "user/-/activities/heart/date/{date}/1d/1min.json".format(
            *self.client._get_common_args(),
            date = format_fitbit_date(date)
        )
        response = self.make_request(url)
        return response['activities-heart-intraday']['dataset']

    def get_devices(self):
        response = self.make_request('user/-/devices.json')
        devices = []
        for device in response:
            if 'id' in device:
                last_sync_time = None
                if 'lastSyncTime' in device:
                    last_sync_time = self.parse_datetime(device.get('lastSyncTime'))
                devices.append({
                    'battery_level': device.get('batteryLevel', None),
                    'id': device.get('id'),
                    'last_sync_time': last_sync_time,
                    'mac': device.get('mac', None),
                    'type': device.get('type', None),
                    'device_version': device.get('deviceVersion', None)
                })
        return devices

    def set_daily_step_goal(self, date, goal):
        new_goal = 5000
        response = self.client.activities_daily_goal(steps=new_goal)

        return response
