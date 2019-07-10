from datetime import datetime, timedelta
from decimal import Decimal
import pytz
from dateutil import parser as dateutil_parser

from fitbit_api.services import FitbitClient, FitbitService, parse_fitbit_date, format_fitbit_date

from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitActivity
from fitbit_activities.models import FitbitActivityType
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitDailyUnprocessedData

class FitbitDayService(FitbitService):

    def __init__(self, date=None, account=None, user=None, username=None, fitbit_day=None, fitbit_user=None):
        if fitbit_day:
            account = fitbit_day.account
        super().__init__(account, user, username, fitbit_user)
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
            try:
                timezone = self.__client.get_timezone()
            except FitbitClient.Unauthorized:
                timezone = pytz.UTC
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
                fitbit_id = activity['logId'],
                account = self.account,
                defaults = {
                    'type': activity_type,
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
        heart_rate_intervals = []
        for interval in self._process_minute_data(data):
            if interval['value'] > 0:
                heart_rate = FitbitMinuteHeartRate(
                    account = self.account,
                    time = interval['datetime'],
                    heart_rate = interval['value']
                )
                heart_rate_intervals.append(heart_rate)

        FitbitMinuteHeartRate.objects.filter(
            account = self.account,
            time__range = [self.day.get_start_datetime(), self.day.get_end_datetime()]
        ).delete()

        FitbitMinuteHeartRate.objects.bulk_create(heart_rate_intervals)
        


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
        return self._process_minute_data(data)

    def _save_unprocessed_data(self, category, data):
        timezone = self.day.get_timezone()
        FitbitDailyUnprocessedData.objects.update_or_create(
            account=self.account,
            day=self.day,
            category = category,
            defaults={
                'payload': data,
                'timezone': timezone.zone
            }
        )

    def _process_minute_data(self, data):
        timezone = self.day.get_timezone()
        
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
        data = self.__client.get_steps(self.date)
        self._save_unprocessed_data('steps', data)
        
        step_intervals = []
        total_steps = 0
        for interval in self._process_minute_data(data):
            if interval['value'] > 0:
                total_steps += interval['value']
                step_intervals.append(FitbitMinuteStepCount(
                    account = self.account,
                    time = interval['datetime'],
                    steps = interval['value']
                ))
        
        FitbitMinuteStepCount.objects.filter(
            account = self.account,
            time__range = [self.day.get_start_datetime(), self.day.get_end_datetime()]
        ).delete()

        FitbitMinuteStepCount.objects.bulk_create(step_intervals)
        return total_steps

    def update_distance(self):
        data = self.__client.get_distance(self.date)
        self._save_unprocessed_data('distance', data)

        total_distance = Decimal(0)
        for interval in self._process_minute_data(data):
            total_distance += Decimal(interval['value'])
        return total_distance

class FitbitStepCountService:

    def __init__(self, user):
        self.user = user        
        self.fitbit_account = FitbitService.get_account(user)

    def get_step_count_between(self, start, end):
        step_counts = FitbitMinuteStepCount.objects.filter(
            account = self.fitbit_account,
            time__range = [start, end]
        ).all()
        total_steps = 0
        for step_count in step_counts:
            total_steps += step_count.steps
        return total_steps

    def is_sedentary_at(self, time):
        step_count = self.get_step_count_between(
            start = time - timedelta(minutes=40),
            end = time
        )
        return False

    def steps_at(self, time):
        return self.get_step_count_between(
            start = time - timedelta(minutes=5),
            end = time
        )

