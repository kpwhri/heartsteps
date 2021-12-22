from django.dispatch import receiver
from django.db.models.signals import post_save

from feature_flags.models import FeatureFlags
from locations.models import Place
from user_event_logs.models import EventLog
from days.services import DayService
from django.db import transaction
from daily_tasks.models import DailyTask
from .models import User
from .constants import TASK_CATEGORY, TASK_PATH, TASK_NAME

def create_step_goal_daily_task(user, hour, minute=0):
    task = DailyTask.create_daily_task(user=user,
                                       category=TASK_CATEGORY,
                                       task=TASK_PATH,
                                       name="{}_{}_{:02}_{:02}".format(user.username, TASK_NAME, hour, minute),
                                       arguments={"username": user.username},
                                       day=None,
                                       hour=hour,
                                       minute=minute)

def delete_step_goal_daily_task(user):
    daily_task_list = DailyTask.objects.filter(user=user, category=TASK_CATEGORY).all()

    for daily_task in daily_task_list:
        daily_task.delete_task()




@receiver(post_save, sender=FeatureFlags)
def FeatureFlags_updated(instance, created, **kwargs):
    # print("FeatureFlags_updated()")
    feature_flags = instance
    
    user = feature_flags.user
    
    # delete daily tasks if they exist
    delete_step_goal_daily_task(user)
    
    if FeatureFlags.has_flag(user, "system_id_stepgoal"):
        # create daily task
        create_step_goal_daily_task(user, 0, 1)