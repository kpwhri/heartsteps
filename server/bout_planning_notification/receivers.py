from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import FirstBoutPlanningTime
from user_event_logs.models import EventLog

from daily_tasks.models import DailyTask
from .models import User
from .constants import TASK_CATEGORY, TASK_PATH, TASK_NAME

def create_daily_task(user, hour):
    task = DailyTask.create_daily_task(user=user,
                                       category=TASK_CATEGORY,
                                       task=TASK_PATH,
                                       name="{}_{}".format(TASK_NAME, hour),
                                       arguments={"username": user.username, "hour": hour},
                                       day=None,
                                       hour=hour,
                                       minute=0)
    
    


def delete_daily_task(user):
    daily_task_list = FirstBoutPlanningTime.get_daily_tasks(user)
    
    for daily_task in daily_task_list:
        daily_task.delete_task()
    


@receiver(post_save, sender=FirstBoutPlanningTime)
def FeatureFlags_updated(instance, created, **kwargs):
    if created:
        EventLog.log(instance.user, "FirstBoutPlanningTime created: {}".format(instance), EventLog.INFO)
        
        # four DailyTasks will be made by three hour gap
        for i in range(instance.hour, instance.hour + 12, 3):
            create_daily_task(instance.user, i)
    else:
        # after deleting the daily tasks,
        delete_daily_task(instance.user)
        first_bout_planning_time = FirstBoutPlanningTime.get(instance.user)
        # four DailyTasks will be newly made by three hour gap
        for i in range(first_bout_planning_time.hour, first_bout_planning_time.hour + 12, 3):
            create_daily_task(instance.user, i)
