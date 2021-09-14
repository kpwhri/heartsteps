from django.db import models

from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from daily_tasks.models import DailyTask
from .constants import TASK_CATEGORY
import uuid

# from activity_summaries.models import Day
from activity_summaries import models as activity_summaries_models

from participants.models import Cohort


class StepGoalPRBScsv(models.Model):
    cohort = models.ForeignKey(Cohort,
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    PRBS_text = models.TextField(blank=True, null=True)
    when_created = models.DateTimeField(auto_now_add=True,
                                        null=True,
                                        blank=True)
    delimiter = models.CharField(max_length=10, default=",")

    def get_seq(cohort):
        query = StepGoalPRBScsv.objects.filter(
            cohort=cohort).order_by("-when_created")

        if query.exists():
            obj = query.first()

            return_list = obj.PRBS_text.split(sep=obj.delimiter)
            return [float(x.strip()) for x in return_list]
        else:
            StepGoalPRBScsv.insert_default(cohort)
            return StepGoalPRBScsv.get_seq(cohort)

    def insert_default(cohort):
        StepGoalPRBScsv.objects.create(
            cohort=cohort,
            PRBS_text=
            '0.3, 0.4, 0.5, 0.3, 0.4, 0.5'
        )


class StepGoal(models.Model):

    class NoSuchUserException(Exception):
        pass

    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date = models.DateField()
    step_goal = models.PositiveIntegerField()

    # @property
    # def id(self):
    #     return str(self.uuid)

    def get(user, date=None):
        query = StepGoal.objects.filter(user=user).order_by('-date')
        
        if date is not None:
            query = query.filter(date=date)
        
        if query.exists():
            return query.first().step_goal
        else:
            raise ValueError("Step Goal does not exist")

    def convert_to_user_obj(user):
        if isinstance(user, str):
            try:
                user_obj = User.objects.get(username=user)
            except User.DoesNotExist:
                raise StepGoal.NoSuchUserException
        elif isinstance(user, User):
            user_obj = user
        else:
            assert isinstance(
                user, User
            ), "user argument should be an instance of User class: {}".format(
                type(user))
        return user_obj

    def get_daily_tasks(user):
        """This will fetch all daily tasks for the user.

        Returns:
            DailyTask[]
        """

        # It converts username to user object (if provided) If User object is provided, it will return the user itself.
        user_obj = StepGoal.convert_to_user_obj(user)

        task_list = DailyTask.search(user=user_obj, category=TASK_CATEGORY)

        return list(task_list)


class ActivityDay(models.Model):
    day = models.ForeignKey(activity_summaries_models.Day,
                            on_delete=models.CASCADE)
