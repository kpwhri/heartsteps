from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import FirstBoutPlanningTime
from locations.models import Place
from user_event_logs.models import EventLog
from days.services import DayService
from django.db import transaction
from daily_tasks.models import DailyTask
from .models import User
from .constants import TASK_CATEGORY, TASK_PATH, TASK_NAME

def create_daily_task(user, hour, minute=0):
    task = DailyTask.create_daily_task(user=user,
                                       category=TASK_CATEGORY,
                                       task=TASK_PATH,
                                       name="{}_{}_{:02}_{:02}".format(user.username, TASK_NAME, hour, minute),
                                       arguments={"username": user.username},
                                       day=None,
                                       hour=hour,
                                       minute=minute)

def delete_daily_task(user):
    daily_task_list = FirstBoutPlanningTime.get_daily_tasks(user)

    for daily_task in daily_task_list:
        daily_task.delete_task()


# create_task should be called by
# user.post_save
# Place.post_save + other Day things
