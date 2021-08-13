
from django.db import models
from django.contrib.auth import get_user_model
# from django_celery_beat.models import PeriodicTask, PeriodicTasks
from daily_tasks.models import DailyTask
from .constants import TASK_CATEGORY
from django.db import models

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