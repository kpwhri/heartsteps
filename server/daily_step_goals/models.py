from django.contrib.auth import get_user
from django.db import models

from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from daily_tasks.models import DailyTask
from .constants import TASK_CATEGORY
import uuid

from activity_summaries import models as activity_summaries_models

from participants.models import Cohort

class StepGoalCalculationSettings(models.Model):
    cohort = models.OneToOneField(Cohort, default=None, on_delete=models.CASCADE)
    magnitude = models.IntegerField(default=4000)
    base_jump = models.IntegerField(default=0)
    maximum = models.IntegerField(default=8000)
    minimum = models.IntegerField(default=2000)
        
    def get(cohort):
        settings, _ = StepGoalCalculationSettings.objects.get_or_create(cohort=cohort)
        
        return settings
            


class StepGoalsEvidence(models.Model):
    user = models.ForeignKey(User, null=False, on_delete = models.CASCADE)
    startdate = models.DateField(null=False)
    enddate = models.DateField(null=False)
    prev_startdate = models.DateField(null=False)
    prev_enddate = models.DateField(null=False)
    base = models.PositiveSmallIntegerField(null=True)
    magnitude = models.IntegerField(default=2000)
    base_jump = models.IntegerField(default=0)
    maximum = models.IntegerField(default=30000)
    minimum = models.IntegerField(default=100)
    evidence = models.JSONField(null=True)
    freetext = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)






class StepGoalSequence(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True)
    order = models.IntegerField(null=True)
    is_used = models.BooleanField(default=False)
    when_created = models.DateTimeField(auto_now_add=True)
    when_used = models.DateTimeField(default=None, null=True)
    sequence_text = models.TextField(default="0.3,0.4,0.5,0.6,0.7,0.8,0.9")
    
    def create(cohort, order=None, sequence_text=None):
        query = StepGoalSequence.objects.filter(cohort=cohort)
        
        if query.exists():
            count = query.count()
        else:
            count = 0
        
        if sequence_text is None:
            return StepGoalSequence.objects.create(cohort=cohort,
                                            order=(order if order is not None else (count + 1)))
        else:
            return StepGoalSequence.objects.create(cohort=cohort,
                                            order=(order if order is not None else (count + 1)),
                                            sequence_text=sequence_text)

class StepGoalSequenceBlock(models.Model):
    cohort = models.OneToOneField(Cohort, on_delete=models.CASCADE, null=True)
    seq_block = models.TextField(null=True, default=None)
    when_created = models.DateTimeField(auto_now_add=True)
    when_used = models.DateTimeField(null=True, default=None)

class StepGoalSequence_User(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    step_goal_sequence = models.OneToOneField(StepGoalSequence, on_delete=models.CASCADE)
    assigned = models.DateTimeField(auto_now_add=True)
    
    

















class StepGoal(models.Model):

    class NoSuchUserException(Exception):
        pass

    uuid = models.UUIDField(primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date = models.DateField()
    step_goal = models.PositiveIntegerField()
    created = models.DateTimeField(null=True, auto_now_add=True)
    
    def get(user, date=None):
        query = StepGoal.objects.filter(user=user).order_by('-date')
        
        if date is not None:
            query = query.filter(date=date).order_by('-created')
        
        if query.exists():
            return query.first().step_goal
        else:
            raise ValueError("Step Goal does not exist")

    # def convert_to_user_obj(user):
    #     if isinstance(user, str):
    #         try:
    #             user_obj = User.objects.get(username=user)
    #         except User.DoesNotExist:
    #             raise StepGoal.NoSuchUserException
    #     elif isinstance(user, User):
    #         user_obj = user
    #     else:
    #         assert isinstance(
    #             user, User
    #         ), "user argument should be an instance of User class: {}".format(
    #             type(user))
    #     return user_obj

    # def get_daily_tasks(user):
    #     """This will fetch all daily tasks for the user.

    #     Returns:
    #         DailyTask[]
    #     """

    #     # It converts username to user object (if provided) If User object is provided, it will return the user itself.
    #     user_obj = StepGoal.convert_to_user_obj(user)

    #     task_list = DailyTask.search(user=user_obj, category=TASK_CATEGORY)

    #     return list(task_list)

