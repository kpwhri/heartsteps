from datetime import datetime, timedelta
from decimal import Decimal
from multiprocessing import Event
import pytz
from dateutil import parser as dateutil_parser
from django.core.exceptions import ImproperlyConfigured

from django.utils import timezone

from fitbit_api.models import FitbitDevice
from fitbit_api.services import FitbitClient, FitbitService, parse_fitbit_date, format_fitbit_date

from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitActivity
from fitbit_activities.models import FitbitActivityType
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitDailyUnprocessedData
from user_event_logs.models import EventLog


class FitbitDayService(FitbitService):
    def __init__(self,
                 date=None,
                 account=None,
                 user=None,
                 username=None,
                 fitbit_day=None,
                 fitbit_user=None):
        if fitbit_day:
            account = fitbit_day.account
        super().__init__(account, user, username, fitbit_user)
        self.__client = FitbitClient(account=self.account)
        if not fitbit_day and not date:
            raise ImproperlyConfigured('No date supplied')
        if date:
            fitbit_day = self.__get_fitbit_day(date)
        self.day = fitbit_day
        self.date = fitbit_day.date

    def __get_fitbit_day(self, date):
        query = FitbitDay.objects.filter(account=self.account, date=date).order_by("created")

        result_count = query.count()

        if result_count == 0:
            try:
                timezone = self.__client.get_timezone()
            except FitbitClient.Unauthorized:
                timezone = pytz.UTC
            created_obj, _ = FitbitDay.objects.update_or_create(account=self.account,
                                            date=date,
                                            _timezone=timezone.zone)
            return created_obj
        else:
            return query.last()

    def update(self):
        current_timezone = self.day.get_timezone()
        new_timezone = self.__client.get_timezone()
        if (current_timezone.zone != new_timezone.zone):
            EventLog.info(None, "[FitbitAccount {}] Timezone update: {} -> {}".format(self.account, current_timezone, new_timezone))
            self.day._timezone = new_timezone.zone
            self.day.save()
        self.day.step_count = self.update_steps()
        self.day._distance = self.update_distance()
        self.update_heart_rate()
        self.update_activities()
        update_devices(self.account)
        
        last_tracker_update = self.account.get_last_tracker_sync_time()
        if last_tracker_update and last_tracker_update > self.day.get_end_datetime(
        ):
            self.day.completely_updated = True
        else:
            self.day.completely_updated = False
        self.day.save()

    def update_activities(self):
        activities = self.__client.get_activities(self.date)
        for activity in activities:
            start_time = dateutil_parser.parse(activity['startTime'])
            end_time = start_time + timedelta(
                milliseconds=activity['duration'])
            average_heart_rate = activity.get('averageHeartRate', 0)
            activity_type, _ = FitbitActivityType.objects.get_or_create(
                fitbit_id=activity['activityTypeId'],
                name=activity['activityName'])
            
            fitbit_id = activity['logId']
            account = self.account
            query = FitbitActivity.objects.filter(fitbit_id=fitbit_id, account=account)

            if query.exists():
                obj = query.last()
                query.update(type=obj.type, average_heart_rate=obj.average_heart_rate, start_time=obj.start_time, end_time=obj.end_time, payload=obj.payload)
            else:
                FitbitActivity.objects.bulk_create([
                    FitbitActivity(
                        fitbit_id=fitbit_id, 
                        account=account, 
                        type=activity_type, 
                        average_heart_rate=average_heart_rate, 
                        start_time=start_time, 
                        end_time=end_time, 
                        payload=activity)
                ])

    def update_heart_rate(self):
        data = self.__client.get_heart_rate(self.date)
        timezone = self.day.get_timezone()
        FitbitDailyUnprocessedData.objects.update_or_create(
            account=self.account,
            day=self.day,
            category='heart rate',
            defaults={
                'payload': data,
                'timezone': timezone.zone
            })
        heart_rate_intervals = []
        intervals = self._process_minute_data(data)
        for interval in intervals:
            if interval['value'] > 0:
                heart_rate = FitbitMinuteHeartRate(
                    account=self.account,
                    time=interval['datetime'],
                    heart_rate=interval['value'])
                heart_rate_intervals.append(heart_rate)
        FitbitMinuteHeartRate.objects.filter(account=self.account,
                                             time__range=[
                                                 self.day.get_start_datetime(),
                                                 self.day.get_end_datetime()
                                             ]).delete()
        FitbitMinuteHeartRate.objects.bulk_create(heart_rate_intervals)
        
    def _get_intraday_time_series(self, activity_type):
        timezone = self.day.get_timezone()
        data = self.__client.get_intraday_activity(activity_type, self.date)
        FitbitDailyUnprocessedData.objects.update_or_create(
            account=self.account,
            day=self.day,
            category=activity_type,
            defaults={
                'payload': data,
                'timezone': timezone.zone
            })
        return self._process_minute_data(data)

    def _save_unprocessed_data(self, category, data):
        timezone = self.day.get_timezone()
        FitbitDailyUnprocessedData.objects.update_or_create(
            account=self.account,
            day=self.day,
            category=category,
            defaults={
                'payload': data,
                'timezone': timezone.zone
            })

    def _process_minute_data(self, data):
        timezone = self.day.get_timezone()

        processed_data = []
        for interval in data:
            interval_datetime = datetime.strptime(
                "%s %s" % (format_fitbit_date(self.date), interval['time']),
                "%Y-%m-%d %H:%M:%S")
            interval_datetime = timezone.localize(interval_datetime)
            processed_data.append({
                'datetime':
                interval_datetime.astimezone(pytz.utc),
                'value':
                interval['value']
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
                step_intervals.append(
                    FitbitMinuteStepCount(account=self.account,
                                          time=interval['datetime'],
                                          steps=interval['value']))

        FitbitMinuteStepCount.objects.filter(account=self.account,
                                             time__range=[
                                                 self.day.get_start_datetime(),
                                                 self.day.get_end_datetime()
                                             ]).delete()

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
        step_counts = self.get_all_step_data_between(start, end)
        total_steps = 0
        for step_count in step_counts:
            total_steps += step_count.steps
        return total_steps

    def get_all_step_data_between(self, start, end):
        return FitbitMinuteStepCount.objects.filter(
            account=self.fitbit_account, time__gte=start, time__lt=end).all()

    def get_all_step_data_json_between(self, start, end):
        step_data_list = self.get_all_step_data_between(start, end)

        return [{"time": x.time, "steps": x.steps} for x in step_data_list]

    def get_all_step_data_list_between(self, start, end):
        assert end > start, "end must be greater than start"

        def get_index(start, time_):
            return int(round((time_-start).total_seconds()/60))

        number_of_minutes = get_index(start, end)

        # print("number_of_minutes: {}".format(number_of_minutes))
        step_list = [0] * number_of_minutes

        all_step_data_between = self.get_all_step_data_between(start, end)
        # print("{}-{}".format(start, end))
        # print(all_step_data_between)

        for a_minute in all_step_data_between:
            index = get_index(start, a_minute.time)
            # print("  a_minute.time: {}, index: {}, a_minute: {}".format(a_minute.time, index, a_minute.__dict__))
            step_list[index] += a_minute.steps

        return step_list

    def is_sedentary_at(self, time):
        step_count = self.get_step_count_between(start=time -
                                                 timedelta(minutes=40),
                                                 end=time)
        return False

    def steps_at(self, time):
        return self.get_step_count_between(start=time - timedelta(minutes=5),
                                           end=time)


def update_devices(account):
    client = FitbitClient(account=account)
    for device in client.get_devices():
        fitbit_device, _ = FitbitDevice.objects.update_or_create(
            account=account,
            fitbit_id=device['id'],
            defaults={
                'device_type': device.get('type', None),
                'device_version': device.get('device_version', None),
                'mac': device.get('mac', None)
            })
        if 'last_sync_time' in device:
            fitbit_device.add_update(time=device['last_sync_time'],
                                     battery_level=device.get(
                'battery_level', None))


class FitbitActivityService(FitbitService):
    class Unauthorized(FitbitClient.Unauthorized):
        pass

    class TooManyRequests(FitbitClient.TooManyRequests):
        pass

    def __init__(self,
                 account=None,
                 user=None,
                 username=None,
                 fitbit_user=None):
        super().__init__(account, user, username, fitbit_user)
        self.__client = FitbitClient(account=self.account)

    def get_days_worn(self, start_date=None):
        if start_date:
            return FitbitDay.objects.filter(account=self.account,
                                            date__gte=start_date,
                                            wore_fitbit=True).count()
        else:
            return FitbitDay.objects.filter(account=self.account,
                                            wore_fitbit=True).count()

    def update(self, date):
        try:
            day_service = FitbitDayService(date=date, account=self.account)
            day_service.update()
        except FitbitClient.Unauthorized as e:
            raise FitbitActivityService.Unauthorized(e)
        except FitbitClient.TooManyRequests as e:
            raise FitbitActivityService.TooManyRequests(e)

    def parse_date(self, date):
        return self.__client.parse_date(date)
