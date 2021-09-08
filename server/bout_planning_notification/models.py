from datetime import datetime
import pytz

from django.db import models, IntegrityError

from django.contrib.auth import get_user_model
# from django_celery_beat.models import PeriodicTask, PeriodicTasks
from daily_tasks.models import DailyTask
from days.services import DayService
from .constants import TASK_CATEGORY
from django.db import models

from user_event_logs.models import EventLog

import random

User = get_user_model()


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

        task_list = DailyTask.search(user=user_obj,
                                     category=TASK_CATEGORY)

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
    
    user = models.ForeignKey(User, on_delete = models.CASCADE)
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
            return_object = Level.objects.create(user=user, date=date, level=Level.DEFAULT)
        EventLog.debug(user, "get({}) returns: {}".format(date, return_object))
        
        return return_object
    
    def exists(user, date):
        """Check if the Level object"""
        return Level.objects.filter(user=user, date=date).exists()
    
    
class RandomDecision(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    random_value = models.FloatField(blank=True, null=True)
    return_bool = models.BooleanField(null=True, default=None)
    
    def create(user):
        obj = RandomDecision.objects.create(user=user, random_value = random.random())
        return obj
        
    def decide(self):
        self.return_bool = (self.random_value < 0.5)
        self.save()
        return self.return_bool

class BoutPlanningDecision(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    N = models.BooleanField(null=True, default=None)
    O = models.BooleanField(null=True, default=None)
    R = models.BooleanField(null=True, default=None)
    return_bool = models.BooleanField(null=True, default=None)
    
    def create(user):
        obj = BoutPlanningDecision.objects.create(user=user)
        return obj
        
    def apply_N(self):
        decision_point_index = self.__get_decision_point_index()
        
        if decision_point_index == 0:
            # TODO: This should be changed to the actual implementation
            yesterday_step_goal = 8000
            # TODO: This should be changed to the actual implementation
            yesterday_step_count = 7999
            
            if yesterday_step_goal <= yesterday_step_count:
                self.N = False
            else:
                self.N = True
        else:
            # TODO: This should be changed to the actual implementation
            today_step_goal = 8000
            
            day_service = DayService(self.user)
            user_local_time = day_service.get_current_datetime()
            prorated_today_step_goal = today_step_goal * (user_local_time.hour * 60 + user_local_time.minute) / 1440
            
            # TODO: This should be changed to the actual implementation
            today_step_count = 0
            
            if prorated_today_step_goal <= today_step_count:
                self.N = False
            else:
                self.N = True
        
        self.save()

    def __get_decision_point_index(self):
        day_service = DayService(self.user)
        # what date & time is it now there?
        user_local_time = day_service.get_current_datetime()
        first_bout_planning_time_obj = FirstBoutPlanningTime.get(self.user)
        diff_in_minutes = (user_local_time.hour * 60 + user_local_time.minute) - first_bout_planning_time_obj.hour * 60
        diff_by_three_hours = round(diff_in_minutes / 180, 0)
        
        if diff_by_three_hours >= 0 and diff_by_three_hours < 4:
            decision_point_index = diff_by_three_hours
        else:
            raise RuntimeError("Unusual time diff: user_local[{}], first_hour[{}]".format(user_local_time, first_bout_planning_time_obj))
        
        return decision_point_index
    
    def apply_O(self):
        self.O = True
        self.save()
    
    def apply_R(self):
        self.R = True
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