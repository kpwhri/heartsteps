from datetime import timedelta, datetime
from dateutil import parser as dateutil_parser
import pytz

from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from fitbit import Fitbit

from fitbit_api.models import FitbitAccount, FitbitSubscription, FitbitDay, FitbitActivity, FitbitActivityType, FitbitMinuteStepCount, FitbitDailyStepsUnprocessed

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
            day = FitbitDay.objects.create(
                account = self.account,
                date = date,
                timezone = self.get_timezone()
            )
        return day

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

        activity_type, _ = FitbitActivityType.objects.get_or_create(
            fitbit_id = activity['activityTypeId'],
            name = activity['activityName']
        )

        FitbitActivity.objects.update_or_create(
            fitbit_id = activity['logId'], defaults={
                'account': self.account,
                'type': activity_type,
                'day': fitbit_day,
                'start_time': start_time,
                'end_time': end_time,
                'vigorous_minutes': self.get_vigorous_minutes(activity),
                'payload': activity
            }
        )

    def get_vigorous_minutes(self, activity):
        vigorous_minutes = 0
        for level in activity.get('activityLevel', []):
            if level['name'] == 'very':
                vigorous_minutes += level['minutes']
        return vigorous_minutes

    def update_steps(self, fitbit_day):
        response = self.client.intraday_time_series('activities/steps', base_date=fitbit_day.format_date())
        
        timezone = fitbit_day.get_timezone()
        FitbitDailyStepsUnprocessed.objects.update_or_create(account=self.account, day=fitbit_day, defaults={
            'payload': response,
            'timezone': timezone.zone
        })
        FitbitMinuteStepCount.objects.filter(account=self.account, day=fitbit_day).delete()
        
        total_steps = 0
        for stepInterval in response['activities-steps-intraday']['dataset']:
            if stepInterval['value'] > 0:
                total_steps += stepInterval['value']
                
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
        fitbit_day.total_steps = total_steps
        fitbit_day.save()
