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

def delete_bout_planning_daily_task(user):
    daily_task_list = FirstBoutPlanningTime.get_daily_tasks(user)
    
    for daily_task in daily_task_list:
        daily_task.delete_task()

def create_bout_planning_daily_task_set(user, hour):
    # fitbit update check
    # DailyTask.create_daily_task(user=user, 
    #                       category="BOUT_PLANNING",
    #                       task="bout_planning_notification.tasks.fitbit_update_check",
    #                       name="{}_{}_{:02}_{:02}".format(user.username, "BoutPlanningNotificationFitbitUpdateCheck", hour - 1, 45),
    #                       arguments={"username": user.username},
    #                       day=None,
    #                       hour=hour - 1,
    #                       minute=45)
    
    # bout planning decision making
    for i in range(hour, hour + 12, 3):
        create_daily_task(user, i)
    DailyTask.create_daily_task(user=user, 
                          category="BOUT_PLANNING",
                          task="bout_planning_notification.tasks.justwalk_daily_ema",
                          name="{}_{}_{:02}_{:02}".format(user.username, "BoutPlanningNotificationDailyEMA", hour + 12, 0),
                          arguments={"username": user.username},
                          day=None,
                          hour=hour+12,
                          minute=0)


@receiver(post_save, sender=FirstBoutPlanningTime)
def FirstBoutPlanningTime_updated(instance, created, **kwargs):
    user = instance.user
        
    if created:
        EventLog.log(instance.user, "FirstBoutPlanningTime created: {}".format(instance), EventLog.INFO)
        
        hour = instance.hour
        create_bout_planning_daily_task_set(user, hour)
    else:
        EventLog.log(instance.user, "FirstBoutPlanningTime updated: {}".format(instance), EventLog.INFO)
        # after deleting the daily tasks,
        delete_bout_planning_daily_task(instance.user)
        first_bout_planning_time = FirstBoutPlanningTime.get(instance.user)
        
        hour = first_bout_planning_time.hour
        create_bout_planning_daily_task_set(user, hour)
            
@receiver(post_save, sender=Place)
@transaction.atomic
def Place_updated(instance, created, **kwargs):
    if instance.type == 'home':
        user = instance.user
        service = DayService(user=user)
        service.update_current_day_timezone_to_default()
        
        EventLog.log(user, "Place is created/updated: {}".format(instance), EventLog.INFO)
        if FirstBoutPlanningTime.exists(user):
            delete_bout_planning_daily_task(user)
            first_bout_planning_time = FirstBoutPlanningTime.get(user)
            # four DailyTasks will be newly made by three hour gap
            
            hour = first_bout_planning_time.hour
            
            create_bout_planning_daily_task_set(user, hour)
