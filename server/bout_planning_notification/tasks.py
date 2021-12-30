import datetime
from celery import shared_task
from days.services import DayService
from fitbit_api.models import FitbitAccountUser
import pytz
from sms_messages.services import SMSService

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
                EventLog.debug(user, "is_necessary() is true. bout planning notification will be sent.")
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
def justwalk_daily_ema(username, parameters=None):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)
    
    if FeatureFlags.exists(user):
        if FeatureFlags.has_flag(user, "bout_planning"):
            EventLog.log(user, "bout planning shared_task has successfully run", EventLog.INFO)
            
            service = BoutPlanningNotificationService(user)
            
            json_survey = JSONSurvey.objects.get(name="daily_ema")
            survey = json_survey.substantiate(user, parameters)
            # survey = service.create_daily_ema()
            
            # message = service.send_notification(title="JustWalk", collapse_subject="bout_planning_survey", survey=survey)
            message = service.send_notification(title="JustWalk", body="How was your day?", collapse_subject="bout_planning_survey", survey=survey)
        else:
            msg = "a user without 'bout_planning' flag came into bout_planning_decision_making: {}=>{}".format(user.username, FeatureFlags.get(user).flags)
            EventLog.log(user, msg, EventLog.ERROR)
            raise BoutPlanningFlagException(msg)
    else:
        msg = "a user without any flag came into bout_planning_decision_making: {}".format(user.username)
        EventLog.log(user, msg, EventLog.ERROR)
        raise BoutPlanningFlagException(msg)
    
@shared_task
def fitbit_update_check(username):
    user = User.objects.get(username=username)
    
    if FeatureFlags.exists(user):
        if FeatureFlags.has_flag(user, "bout_planning"):
            try:
                fitbit_account = FitbitAccountUser.objects.get(user=user).account
                
                last_update = fitbit_account.last_updated
                
                if last_update:
                    now = datetime.datetime.now().astimezone(pytz.utc)
                    diff = now - last_update
                    EventLog.info(user, "user={}, last_update={}, update_gap={}".format(username, last_update, diff))
                    
                    if diff > datetime.timedelta(minutes=60):
                        EventLog.info(user, "Recent Fitbit Update Doesn't Exist. SMS message should be sent.")
                        sms_service = SMSService(user=user)
                        timegap_str = ""
                        if diff > datetime.timedelta(hours=36):
                            timegap_str = "a while"
                        elif diff > datetime.timedelta(hours=12):
                            timegap_str = "a day"
                        elif diff > datetime.timedelta(minutes=90):
                            timegap_str = "a few hours"
                        else:
                            timegap_str = "a while"
                            
                        greeting = ""
                        day_service = DayService(user)
                        local_time = day_service.get_current_datetime()
                        if local_time.hour < 12 and local_time.hour > 3:
                            greeting = "Good morning! "
                        elif local_time.hour < 16 and local_time.hour >= 12:
                            greeting = "Good afternoon. "
                        elif local_time.hour < 22 and local_time.hour >= 16:
                            greeting = "Good evening. "
                        else:
                            pass
                        
                        msg = "[JustWalk] {}It's been {} since the last data was uploaded. Please click the following link to upload.\n\nfitbit://about".format(greeting, timegap_str)
                        sms_message = sms_service.send(msg)
                        EventLog.info(user, "SMS message is sent: {}".format(msg))
                        EventLog.info(user, "SMS message is sent: {}".format(sms_message.__dict__))
                        
                    else:
                        EventLog.info(user, "Recent Fitbit Update Exists. No SMS message should be sent.")
                        
                    
                    
                    
                        
                else:
                    EventLog.error(user, "No device update record")
            except Exception as e:
                EventLog.error(user, "Exception occurred during Fitbit Last Update Check: {}".format(e))
                raise e
        else:
            msg = "a user without 'bout_planning' flag came in: {}=>{}".format(user.username, FeatureFlags.get(user).flags)
            EventLog.log(user, msg, EventLog.ERROR)
            raise BoutPlanningFlagException(msg)
    else:
        msg = "a user without any flag came in: {}".format(user.username)
        EventLog.log(user, msg, EventLog.ERROR)
        raise BoutPlanningFlagException(msg)
    