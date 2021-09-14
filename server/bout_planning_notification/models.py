from datetime import datetime, timedelta, date
import pytz
import math

from django.db import models, IntegrityError

from django.contrib.auth import get_user_model
# from django_celery_beat.models import PeriodicTask, PeriodicTasks
from daily_tasks.models import DailyTask
from days.services import DayService
from .constants import TASK_CATEGORY
from django.db import models

from user_event_logs.models import EventLog
from participants.models import Participant
from daily_step_goals.services import StepGoalsService
from activity_summaries.models import Day
import random

from fitbit_api.models import FitbitAccountUser
from fitbit_activities.models import FitbitMinuteStepCount
            


User = get_user_model()

def force_str(obj):
    if isinstance(obj, str):
        return "\"{}\"".format(obj)
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, list):
        return "[{}]".format(",".join(list(map(lambda x: force_str(x), obj))))
    elif isinstance(obj, dict):
        return "{{{}}}".format(",".join(list(map(lambda x: "\"{}\": {}".format(x, force_str(obj[x])), obj))))
    else:
        return str(obj)


class FirstBoutPlanningTime(models.Model):
    class FirstBoutPlanningTimeExistException(Exception):
        pass

    class FirstBoutPlanningTimeDoNotExistException(Exception):
        pass

    class NoSuchUserException(Exception):
        pass

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    hour = models.IntegerField(default=7)
    minute = models.IntegerField(default=0)

    active = models.BooleanField(default=True)

    def __str__(self):
        if self.active:
            return "FirstBoutPlanningTime = {} ({})".format(
                self.time, self.user)
        else:
            return "Not active ({})".format(self.user)

    @property
    def time(self):
        return "{:02}:{:02}".format(self.hour, self.minute)

    @property
    def data_dict(self):
        return {'time': self.time}

    def __is_formatted_properly(time):
        assert isinstance(time, str), "time must be a string"

        try:
            FirstBoutPlanningTime.__parse(time)
            return True
        except:
            return False

    def __parse(time):
        assert isinstance(time, str), "time must be a string"
        time_list = time.split(':')
        if len(time_list) != 2:
            raise ValueError("wrong time string: {}".format(time))
        try:
            hour = int(time_list[0])
            minute = int(time_list[1])

            if hour in range(0, 24) and minute in range(0, 60):
                return (hour, minute)
            else:
                raise ValueError("wrong time string: {}".format(time))
        except:
            raise ValueError("wrong time string: {}".format(time))

    def convert_to_user_obj(user):
        if isinstance(user, str):
            try:
                user_obj = User.objects.get(username=user)
            except User.DoesNotExist:
                raise FirstBoutPlanningTime.NoSuchUserException
        elif isinstance(user, User):
            user_obj = user
        else:
            assert isinstance(
                user, User
            ), "user argument should be an instance of User class: {}".format(
                type(user))
        return user_obj

    def __get_base_query(user):
        """returns the base query of the FirstBoutPlaningTime object"""

        return FirstBoutPlanningTime.objects.filter(user=user, active=True)

    def exists(user):
        """check if the first bout planning time exists

        Args:
            user (User or str)
            
        Raises:
            FirstBoutPlanningTime.NoSuchUserException : if the username is wrong

        Returns:
            boolean: if the first bout planning time exist
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)

        return FirstBoutPlanningTime.__get_base_query(user_obj).exists()

    def create(user, time="07:00"):
        """Create a new first bout planning time.
        
        Arguments: 
            user(User or str)
            time(str) optional
        
        Raises:
            FirstBoutPlanningTime.FirstBoutPlanningTimeExistException : if the first bout planning time exists
            FirstBoutPlanningTime.NoSuchUserException : if the username is wrong
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)
        assert isinstance(time,
                          str), "time argument should be a string: {}".format(
                              type(time))
        assert FirstBoutPlanningTime.__is_formatted_properly(
            time), "time should be correctly formated: {}".format(time)

        (hour, minute) = FirstBoutPlanningTime.__parse(time)

        if FirstBoutPlanningTime.exists(user_obj):
            raise FirstBoutPlanningTime.FirstBoutPlanningTimeExistException

        return FirstBoutPlanningTime.objects.create(user=user_obj,
                                                    hour=hour,
                                                    minute=minute)

    def update(user: User, time: str):
        """updates if the first bout planning time exists

        Args:
            user (User or str)
            time (str): new time

        Raises:
            FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException: if the featureFlags do not exist
            FirstBoutPlanningTime.NoSuchUserException: if the user does not exist

        Returns:
            FirstBoutPlanningTime object: updated first bout planning time
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)
        assert isinstance(time,
                          str), "time argument should be a string: {}".format(
                              type(time))
        assert FirstBoutPlanningTime.__is_formatted_properly(
            time), "time should be correctly formated: {}".format(time)

        if not FirstBoutPlanningTime.exists(user_obj):
            raise FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException

        (hour, minute) = FirstBoutPlanningTime.__parse(time)

        obj = FirstBoutPlanningTime.get(user_obj)
        obj.hour = hour
        obj.minute = minute
        obj.save()

        return obj

    def get(user: User):
        """tries to get the first bout planning time 

        Args:
            user (User or str)

        Raises:
            FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException: if the first bout planning time do not exist.
            FirstBoutPlanningTime.NoSuchUserException : if the username is wrong
            
        Returns:
            FeatureFlag object
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)

        if not FirstBoutPlanningTime.exists(user_obj):
            raise FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException

        return FirstBoutPlanningTime.__get_base_query(user_obj).get()

    def get_daily_tasks(user):
        """This will fetch all daily tasks for the user.
        
        Returns:
            DailyTask[]
        """

        # It converts username to user object (if provided) If User object is provided, it will return the user itself.
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)

        task_list = DailyTask.search(user=user_obj, category=TASK_CATEGORY)

        return list(task_list)


class Level(models.Model):

    RECOVERY = 'RE'
    RANDOM = 'RA'
    NO = 'NO'
    NR = 'NR'
    FULL = 'FU'

    DEFAULT = FULL

    LEVELS = [
        (RECOVERY, 'RE'),
        (RANDOM, 'RA'),
        (NO, 'NO'),
        (NR, 'NR'),
        (FULL, 'FU'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVELS)
    date = models.DateField()

    def __str__(self):
        return "{} @ {}".format(self.level, self.date)

    def create(user, level, date=None):
        """Create a new Level"""
        if date is None:
            day_service = DayService(user)

            # what date is it now there?
            date = day_service.get_current_date()
        if Level.exists(user, date):
            raise IntegrityError('Level already exists')
        else:
            return Level.objects.create(user=user, date=date, level=level)

    def get(user, date=None):
        """Get a Level object"""
        EventLog.debug(user, "get({}) is called".format(date))
        if date is None:
            day_service = DayService(user)

            # what date is it now there?
            date = day_service.get_current_date()

        if Level.exists(user, date):
            return_object = Level.objects.get(user=user, date=date)
        else:
            return_object = Level.objects.create(user=user,
                                                 date=date,
                                                 level=Level.DEFAULT)
        EventLog.debug(user, "get({}) returns: {}".format(date, return_object))

        return return_object

    def exists(user, date):
        """Check if the Level object"""
        return Level.objects.filter(user=user, date=date).exists()


class RandomDecision(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    random_value = models.FloatField(blank=True, null=True)
    return_bool = models.BooleanField(null=True, default=None)

    def create(user):
        obj = RandomDecision.objects.create(user=user,
                                            random_value=random.random())
        return obj

    def decide(self):
        self.return_bool = (self.random_value < 0.5)
        self.save()
        return self.return_bool


class BoutPlanningDecision(models.Model):
    WEEKDAY_WEEKEND = 'weekday/weekend'
    DAY_BY_DAY = 'day by day'
    DAY_OF_A_WEEK = 'day of a week'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    N = models.BooleanField(null=True, default=None)
    O = models.BooleanField(null=True, default=None)
    R = models.BooleanField(null=True, default=None)
    return_bool = models.BooleanField(null=True, default=None)
    data = models.JSONField(null=True, default=None)
    when_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def create(user):
        obj = BoutPlanningDecision.objects.create(user=user, data={})
        return obj

    def apply_N(self):
        decision_point_index = self.__get_decision_point_index()
        self.data['decision_point_index'] = decision_point_index

        day_service = DayService(user=self.user)
        today = day_service.get_current_date()
        yesterday = today - timedelta(days=1)
        self.data['today'] = force_str(today)
        self.data['yesterday'] = force_str(yesterday)
        step_goals_service = StepGoalsService(self.user)
            
        if decision_point_index == 0:
            yesterday_step_goal = step_goals_service.get_step_goal(date=yesterday)
            self.data['yesterday_step_goal'] = yesterday_step_goal
            
            yesterday_activity_summary = Day.get(user=self.user, date=yesterday)
            if yesterday_activity_summary:
                yesterday_step_count = yesterday_activity_summary.steps
            else:
                yesterday_step_count = 0
            self.data['yesterday_step_count'] = yesterday_step_count

            if yesterday_step_goal <= yesterday_step_count:
                self.N = False
            else:
                self.N = True
        else:
            today_step_goal = step_goals_service.get_step_goal(date=today)
            self.data['today_step_goal'] = today_step_goal
            
            user_local_time = self.__get_user_local_time()
            self.data['user_local_time'] = str(user_local_time)
            
            prorated_today_step_goal = today_step_goal * (
                user_local_time.hour * 60 + user_local_time.minute) / 1440
            self.data['prorated_today_step_goal'] = prorated_today_step_goal
            
            # TODO: Check if this works during the day
            today_activity_summary = Day.get(user=self.user, date=today)
            if today_activity_summary:
                today_step_count = today_activity_summary.steps
            else:
                today_step_count = 0
            
            self.data['today_step_count'] = today_step_count
            
            if prorated_today_step_goal <= today_step_count:
                self.N = False
            else:
                self.N = True

        self.save()

    def apply_O(self):
        criteria = [{
            'minimum': 0,
            'maximum': 7,
            'mode': BoutPlanningDecision.WEEKDAY_WEEKEND,
            'fetch_period': 3,
            'window_size': 3,
            'threshold1': 0.55,
            'threshold2': 0.5
        }, {
            'minimum': 8,
            'maximum': 21,
            'mode': BoutPlanningDecision.WEEKDAY_WEEKEND,
            'fetch_period': 8,
            'window_size': 3,
            'threshold1': 0.55,
            'threshold2': 0.6
        }, {
            'minimum': 22,
            'maximum': 9999,
            'mode': BoutPlanningDecision.DAY_BY_DAY,
            'fetch_period': 5,
            'window_size': 3,
            'threshold1': 0.55,
            'threshold2': 0.55
        }]

        study_day_index = self.__get_study_day_index()
        self.data['study_day_index'] = study_day_index
        
        criterion = self.__get_criterion(study_day_index, criteria)
        self.data['criterion'] = criterion
        
        fetch_periods = self.__get_fetch_periods(study_day_index, criterion)
        
        self.data['fetch_periods'] = force_str(fetch_periods)
        
        walkdata_list = self.__fetch_walkdata(fetch_periods)
        
        self.O = self.__process_walkdata(criterion, walkdata_list)

        self.save()

    def apply_R(self):
        def fetch_bout_planning_notification_logs(days=3):
            # TODO: This should be changed to the actual implementation
            return [
                {
                    "when": datetime(2021, 9, 8, 7, 0, 0)
                },
                {
                    "when": datetime(2021, 9, 8, 10, 0, 0)
                },
                {
                    "when": datetime(2021, 9, 8, 13, 0, 0)
                },
                {
                    "when": datetime(2021, 9, 9, 7, 0, 0)
                }
            ]

        def convert_logs_to_time_list(logs):
            time_list = []
            
            for log_item in logs:
                time_list.append({
                    "start": log_item['when'],
                    "end": log_item['when'] + timedelta(minutes=180)
                })
            return time_list

        def count_receptive_activity(activity_list, log_time_list):
            consecutive_minutes_criteria = 5    # activity consists of 5 consecutive minutes of ...
            active_minute_criteria = 100    # 100 steps per minute
            
            number_of_receptive_activity = 0
            
            for index, activity in enumerate(activity_list):
                padded_walkdata = self.__pad_walkdata(activity['raw_data'])
                
                current_log_time = log_time_list[index]
                
                if activity['date']['start'].date() == current_log_time['start'].date():
                    start_index = current_log_time['start'].hour * 60 + current_log_time['start'].minute
                    end_index = start_index + 180
                    
                    cumulative_active_minutes = 0
                    for i in range(start_index, end_index):
                        if padded_walkdata[i] > active_minute_criteria: # if they walked 100 steps or more
                            cumulative_active_minutes += 1
                            if cumulative_active_minutes >= consecutive_minutes_criteria:
                                number_of_receptive_activity += 1
                                break
                        else:
                            cumulative_active_minutes = 0   # reset
            
            return number_of_receptive_activity

        budget = 0.5  # 50% of decision points
        self.data['budget'] = budget
        
        receptive_criteria = 0.3  # +30% of notification is responded favorably
        self.data['receptive_criteria'] = receptive_criteria
        
        # # of notification | minimum # of favorable response to be marked as "receptive"
        #                 1 | 1
        #                 2 | 1
        #                 3 | 1
        #                 4 | 2
        #                 5 | 2
        #                 6 | 2
        #                 7 | 3
        #                 8 | 3
        #                 9 | 3
        #                10 | 3
        #                11 | 4
        #                12 | 4

        logs = fetch_bout_planning_notification_logs(days=3)
        self.data['logs'] = force_str(logs)
        
        if len(logs) >= budget * 12:
            # the budget is all used up.
            self.R = False
        else:
            log_time_list = convert_logs_to_time_list(logs)
            self.data['log_time_list'] = force_str(log_time_list)
            
            activity_list = self.__fetch_walkdata(log_time_list)
            self.data['activity_list'] = force_str(activity_list)
            
            number_of_receptive_activity = count_receptive_activity(
                activity_list, log_time_list)
            self.data['number_of_receptive_activity'] = number_of_receptive_activity
            
            minimum_number_of_activity = math.ceil(
                len(log_time_list) * receptive_criteria)
            self.data['minimum_number_of_activity'] = minimum_number_of_activity
            
            if number_of_receptive_activity >= minimum_number_of_activity:
                self.R = True
            else:
                self.R = False
        self.save()

    def decide(self):
        self.return_bool = True
        if self.N is not None:
            self.return_bool = self.return_bool & self.N
        if self.O is not None:
            self.return_bool = self.return_bool & self.O
        if self.R is not None:
            self.return_bool = self.return_bool & self.R

        self.save()
        return self.return_bool

    def __get_user_local_time(self):
        day_service = DayService(self.user)
        user_local_time = day_service.get_current_datetime()
        return user_local_time

    def __get_decision_point_index(self):
        user_local_time = self.__get_user_local_time()
        self.data['user_local_time'] = force_str(user_local_time)
        first_bout_planning_time_obj = FirstBoutPlanningTime.get(self.user)
        diff_in_minutes = (user_local_time.hour * 60 + user_local_time.minute
                           ) - first_bout_planning_time_obj.hour * 60
        diff_by_three_hours = int(round(diff_in_minutes / 180, 0))

        if diff_by_three_hours >= 0 and diff_by_three_hours < 4:
            decision_point_index = diff_by_three_hours
        else:
            raise RuntimeError(
                "Unusual time diff: user_local[{}], first_hour[{}]".format(
                    user_local_time, first_bout_planning_time_obj))

        return decision_point_index

    def __get_study_day_index(self):
        def get_study_start_date():
            participant = Participant.objects.filter(user=self.user)
            if participant and participant.exists():
                return participant.first().study_start_date
            else:
                raise ValueError("No Participant under user: {}".format(
                    self.user))

        study_start_date = get_study_start_date()
        user_local_date = self.__get_user_local_time().date()

        date_diff = user_local_date - study_start_date

        return date_diff.days

    def __get_criterion(self, study_day_index, criteria):
        for criterion in criteria:
            if 'minimum' in criterion:
                if criterion['minimum'] > study_day_index:
                    continue
            if 'maximum' in criterion:
                if criterion['maximum'] < study_day_index:
                    continue

            # returning a new copy in the memory of the criterion
            return dict(criterion)
        raise ValueError(
            "Could not find criterion that matches study_day_index: {}".format(
                study_day_index))

    def __get_fetch_periods(self, study_day_index, criterion):
        def is_weekday(a_day):
            return a_day.weekday() in (5, 6)

        user_local_date = self.__get_user_local_time().date()

        if criterion['mode'] == BoutPlanningDecision.WEEKDAY_WEEKEND:
            is_today_weekday = is_weekday(user_local_date)

            days_list = []
            date_cursor = user_local_date - timedelta(days=1)

            if 'fetch_period' in criterion:
                while True:
                    if is_weekday(date_cursor) == is_today_weekday:
                        days_list.append(date_cursor)
                    if len(days_list) == criterion['fetch_period']:
                        break
                    if len(days_list) > 99:  # it is fetching too many days
                        raise ValueError(
                            'fetch_period should be lower than 99: {}'.format(
                                criterion['fetch_period']))
                    date_cursor = date_cursor - timedelta(days=1)
            else:
                raise ValueError('fetch_period must be in the criteria')

        elif criterion['mode'] == BoutPlanningDecision.DAY_BY_DAY:
            days_list = []
            date_cursor = user_local_date - timedelta(days=1)

            if 'fetch_period' in criterion:
                while True:
                    days_list.append(date_cursor)
                    if len(days_list) == criterion['fetch_period']:
                        break
                    if len(days_list) > 99:  # it is fetching too many days
                        raise ValueError(
                            'fetch_period should be lower than 99: {}'.format(
                                criterion['fetch_period']))
                    date_cursor = date_cursor - timedelta(days=1)
            else:
                raise ValueError('fetch_period must be in the criteria')
        elif criterion['mode'] == BoutPlanningDecision.DAY_OF_A_WEEK:
            todays_weekday = user_local_date.weekday()

            days_list = []
            date_cursor = user_local_date - timedelta(days=1)

            if 'fetch_period' in criterion:
                while True:
                    if date_cursor.weekday() == todays_weekday:
                        days_list.append(date_cursor)
                    if len(days_list) == criterion['fetch_period']:
                        break
                    if len(days_list) > 99:  # it is fetching too many days
                        raise ValueError(
                            'fetch_period should be lower than 99: {}'.format(
                                criterion['fetch_period']))
                    date_cursor = date_cursor - timedelta(days=1)
            else:
                raise ValueError('fetch_period must be in the criteria')
        else:
            raise ValueError("Unknown criterion mode: {}".format(
                criterion['mode']))

        return days_list

    def __fetch_walkdata(self, fetch_periods):
        def fetch_walkdata(date=None):
            # day_service = DayService(self.user)
            # if date is None:
            #     date = day_service.get_current_date()
            
            # day_start = day_service.get_start_of_day(date)
            # day_end = day_service.get_end_of_day(date)
            
            # TODO: This should be changed to the actual implementation
            
            # fitbit_account = FitbitAccountUser.get_account(self.user)
            # walkdata_list = [
            #     {
            #         'when': {
            #             'hour': x.time.hour, 
            #             'minute': x.time.minute
            #         },
            #         'steps': x.steps
            #     } for x in FitbitMinuteStepCount.objects.filter(account=fitbit_account, time__gte=day_start, time__lte=day_end).order_by('time').all()
            # ]
            
            walkdata_list = []
            for i in range(0, 100):
                walkdata_list.append({
                    'when': {
                        'hour': random.randint(0, 24),
                        'minute': random.randint(0, 60)
                    },
                    'steps': random.randint(30, 150)
                })

            return walkdata_list

        raw_walk_data = []
        for a_day in fetch_periods:
            raw_walk_data.append({
                'date': a_day,
                'raw_data': fetch_walkdata(a_day)
            })

        return raw_walk_data

    def __process_walkdata(self, criterion, walkdata_list):
        def ifthisthenthat(this, that, it):
            if this:
                return that
            else:
                return it

        def calculate_moving_average(criterion, padded_walkdata):
            half_window_size = criterion['window_size']
            window_size = half_window_size * 2 + 1
                # average should be over threshold1. instead of dividing
                # by window size, the threshold is pre-calculated for the speed
            threshold1 = criterion['threshold1'] * window_size

            moving_averaged_walkdata = [0] * 1440
                # for time complexity of O(n), moving average became more complex
            current_sum = sum(padded_walkdata[0:window_size])
            moving_averaged_walkdata[half_window_size - 1] = ifthisthenthat(
                    current_sum > threshold1, 1, 0)

            for i in range(half_window_size, 1440 - half_window_size):
                current_sum = current_sum + padded_walkdata[
                        i + half_window_size -
                        1] - padded_walkdata[i - half_window_size]
                moving_averaged_walkdata[i] = ifthisthenthat(
                        current_sum > threshold1, 1, 0)
                    
            return moving_averaged_walkdata
    
        activity_list = []

        # 0. Prepare to Pick the right 3-hour window
        decision_point_index = self.__get_decision_point_index()
        first_bout_planning_time = FirstBoutPlanningTime.get(self.user).hour
        start_index = int(
            (first_bout_planning_time + decision_point_index * 3) * 60)
        finish_index = start_index + 180
        # 1. padding with zeros, reorganizing overlapped step data
        # sometimes, Fitbit overlapses/jump minute step data when the timezone changes
        for walkdata in walkdata_list:
            padded_walkdata = self.__pad_walkdata(walkdata['raw_data'])

            # 2. moving-averaging and applying threshold 1
            moving_averaged_walkdata = calculate_moving_average(criterion, padded_walkdata)

            # 3. Pick up proper timespan, check if there's an activity
            if_activity_exists = max(
                moving_averaged_walkdata[start_index:finish_index])
            activity_list.append(if_activity_exists)

        # 4. If we average all activities, is the three-hour window active?
        if len(activity_list) > 0:
            average_activity = sum(activity_list) / len(activity_list)
            if average_activity > criterion['threshold2']:
                return True
            else:
                return False
        else:
            # TODO: Discuss about this case - what if there is no data available?
            return True

    def __pad_walkdata(self, walkdata):
        padded_walkdata = [0] * 1440  # total number of minutes in a day
        for minute_data in walkdata:
            when = minute_data['when']
            steps = minute_data['steps']

            minute_index = when['hour'] * 24 + when['minute']
            padded_walkdata[minute_index] += steps
        return padded_walkdata