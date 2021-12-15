from celery import shared_task

from .models import BoutPlanningMessage, JSONSurvey, User
from .services import BoutPlanningNotificationService

from user_event_logs.models import EventLog
from feature_flags.models import FeatureFlags

class BoutPlanningFlagException(Exception):
    pass

@shared_task
def send_bout_planning_survey(username):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)
    
    if not FeatureFlags.exists(user):
        raise Exception("The user does not have a feature flag.")
    
    if not FeatureFlags.has_flag(user, "bout_planning"):
        raise Exception("The user does not have 'bout_planning' flag.")
    
    service = BoutPlanningNotificationService(user)
    
    survey = service.create_survey()
    
    body = pull_random_bout_planning_message()
    
    message = service.send_notification(title="JustWalk", collapse_subject="bout_planning_survey", body=body, survey=survey)

def pull_random_bout_planning_message():
    if BoutPlanningMessage.objects.exists():
        body = BoutPlanningMessage.objects.order_by('?').first().message
    else:
        body = "Feeling stressed? Do you think a quick walk might help?"
    return body
        
        
@shared_task
def bout_planning_decision_making(username):
    """Main logic for bout planning decision making. This runs every three hours
    task id: bout_planning_notification.tasks.bout_planning_decision_making
    """
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)
    
    if FeatureFlags.exists(user):
        if FeatureFlags.has_flag(user, "bout_planning"):
            EventLog.log(user, "bout planning shared_task has successfully run", EventLog.INFO)
            
            service = BoutPlanningNotificationService(user)
            
            if service.is_necessary():
                survey = service.create_survey()
                body = pull_random_bout_planning_message()
                
                message = service.send_notification(title="JustWalk", collapse_subject="bout_planning_survey", body=body, survey=survey)
                EventLog.success(user, "bout planning notification is sent.")
            else:
                EventLog.debug(user, "is_necessary() is false. bout planning notification is not sent.")
        else:
            msg = "a user without 'bout_planning' flag came into bout_planning_decision_making: {}=>{}".format(user.username, FeatureFlags.get(user).flags)
            EventLog.log(user, msg, EventLog.ERROR)
            raise BoutPlanningFlagException(msg)
    else:
        msg = "a user without any flag came into bout_planning_decision_making: {}".format(user.username)
        EventLog.log(user, msg, EventLog.ERROR)
        raise BoutPlanningFlagException(msg)
    
@shared_task
def justwalk_daily_ema(username):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)
    
    if FeatureFlags.exists(user):
        if FeatureFlags.has_flag(user, "bout_planning"):
            EventLog.log(user, "bout planning shared_task has successfully run", EventLog.INFO)
            
            service = BoutPlanningNotificationService(user)
            
            json_survey = JSONSurvey.objects.get(name="JustWalk JITAI Daily EMA")
            survey = json_survey.substantiate(user)
            # survey = service.create_daily_ema()
            
            # message = service.send_notification(title="JustWalk", collapse_subject="bout_planning_survey", survey=survey)
            message = service.send_notification(title="JustWalk", collapse_subject="bout_planning_survey")
        else:
            msg = "a user without 'bout_planning' flag came into bout_planning_decision_making: {}=>{}".format(user.username, FeatureFlags.get(user).flags)
            EventLog.log(user, msg, EventLog.ERROR)
            raise BoutPlanningFlagException(msg)
    else:
        msg = "a user without any flag came into bout_planning_decision_making: {}".format(user.username)
        EventLog.log(user, msg, EventLog.ERROR)
        raise BoutPlanningFlagException(msg)
    