import datetime
from celery import shared_task
from days.services import DayService
from fitbit_api.models import FitbitAccountUser
import pytz
from participants.services import ParticipantService
from daily_step_goals.tasks import send_daily_step_goal_notification
from participants.models import Cohort, Participant
from sms_messages.services import SMSService

from django.core.mail import send_mail
from django.conf import settings

from .models import BoutPlanningMessage, JSONSurvey, User
from .services import BoutPlanningNotificationService

from push_messages.models import Device
from user_event_logs.models import EventLog
from feature_flags.models import FeatureFlags

class BoutPlanningFlagException(Exception):
    pass

def get_baseline_complete_info():
    from participants.models import Cohort, Participant
    from participants.services import ParticipantService
    cohort_name = 'JustWalk'
    cohort = Cohort.objects.filter(name=cohort_name).first()
    query = Participant.objects.filter(cohort=cohort)
    for participant in query.all():
        service = ParticipantService(participant=participant)
        is_baseline_complete = service.is_baseline_complete()
        print("{}\t{}".format(participant.heartsteps_id, is_baseline_complete))

def get_collapse_subject(prefix):
    return "{}_{}".format(prefix, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

@shared_task
def send_bout_planning_survey(username):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)
    
    if user.is_active:
        if not FeatureFlags.exists(user):
            raise Exception("The user does not have a feature flag.")
        
        if not FeatureFlags.has_flag(user, "bout_planning"):
            raise Exception("The user does not have 'bout_planning' flag.")
        
        service = BoutPlanningNotificationService(user)
        
        survey = service.create_survey()
        
        body = pull_random_bout_planning_message()
        
        message = service.send_notification(title="JustWalk", collapse_subject=get_collapse_subject("bps1"), body=body, survey=survey)

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
    if user.is_active:
        if FeatureFlags.exists(user):
            if FeatureFlags.has_flag(user, "bout_planning"):
                EventLog.log(user, "bout planning shared_task has successfully run", EventLog.INFO)

                participant_service = ParticipantService(user=user)
                if participant_service.is_baseline_complete():
                    service = BoutPlanningNotificationService(user)
                    
                    if not service.has_sequence_assigned():
                        service.assign_level_sequence(participant_service.participant.cohort, user=user)

                    if service.is_this_redundant_thread():
                        EventLog.error(user, "redundant execution is happening")
                    else:
                        if service.is_necessary():
                            survey = service.create_survey()
                            body = pull_random_bout_planning_message()
                            
                            message = service.send_notification(title="JustWalk", collapse_subject=get_collapse_subject("bps2"), body=body, survey=survey)
                            EventLog.success(user, "bout planning notification is sent.")
                        else:
                            EventLog.success(user, "is_necessary() is false. bout planning notification is not sent.")
                else:
                    EventLog.success(user, "is_baseline_complete() is false. bout planning notification is not sent.")
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
    if user.is_active:
        if FeatureFlags.exists(user):
            if FeatureFlags.has_flag(user, "bout_planning"):
                EventLog.log(user, "bout planning shared_task has successfully run", EventLog.INFO)
                
                participant_service = ParticipantService(user=user)
                if participant_service.is_baseline_complete():
                    service = BoutPlanningNotificationService(user)
                    
                    json_survey = JSONSurvey.objects.get(name="daily_ema")
                    if service.check_last_survey_datetime(suffix="daily_ema"):
                        survey = json_survey.substantiate(user, parameters)
                        # survey = service.create_daily_ema()
                        
                        # message = service.send_notification(title="JustWalk", collapse_subject="bout_planning_survey", survey=survey)
                        # message = service.send_notification(title="JustWalk", body="How was your day?", collapse_subject="bout_planning_survey", survey=survey)
                        message = service.send_notification(title="JustWalk", body="Time to think and prepare for tomorrow's activity.", collapse_subject=get_collapse_subject("de1"), survey=survey)
                    else:
                        EventLog.info(user, "The same daily_ema has been sent in less than 23 hours.")
                else:
                    EventLog.info(user, "is_baseline_complete() is false. bout planning notification is not sent.")
            else:
                msg = "a user without 'bout_planning' flag came into bout_planning_decision_making: {}=>{}".format(user.username, FeatureFlags.get(user).flags)
                EventLog.log(user, msg, EventLog.ERROR)
                raise BoutPlanningFlagException(msg)
        else:
            msg = "a user without any flag came into bout_planning_decision_making: {}".format(user.username)
            EventLog.log(user, msg, EventLog.ERROR)
            raise BoutPlanningFlagException(msg)

def get_fitbit_account(user):
    '''returns the Fitbit account associated with the user. If the account is not available, returns None'''
    query = FitbitAccountUser.objects.filter(user=user)

    if query.exists() and query.count() == 1:
        return query.first().account
    else:
        return None

def raise_exceptions_if_inappropriate(user) -> bool:
    '''returns True if user is good to go for JustWalk study and has the "bout_planning" feature flag'''
    if not user.is_active:
        EventLog.info(user, "[fitbit_update_check] The user is not active")
        return False
    
    if not FeatureFlags.exists(user):
        msg = "a user without any flag came in: {}".format(user.username)
        EventLog.log(user, msg, EventLog.ERROR)
        raise BoutPlanningFlagException(msg)
    
    if not FeatureFlags.has_flag(user, "bout_planning"):
        msg = "a user without 'bout_planning' flag came in: {}=>{}".format(user.username, FeatureFlags.get(user).flags)
        EventLog.log(user, msg, EventLog.ERROR)
        raise BoutPlanningFlagException(msg)
        
    fitbit_account = get_fitbit_account(user)
    if not fitbit_account:
        EventLog.info(user, "Fitbit Account that correspods to username {} does not exist".format(user.username))
        return False
        
    return True

def send_mail_to_justwalk_staff(title, message, recipient_type=None):
    if recipient_type == 'tech':
        recipient_list = ['jup014@eng.ucsd.edu']
    elif recipient_type == 'staff':
        recipient_list = ['justwalk@ucsd.edu']
    else:
        recipient_list = ['jup014@eng.ucsd.edu', 'justwalk@ucsd.edu']
    
    send_mail(subject=title, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=recipient_list)

def check_if_device_connected(user):
    query = Device.objects.filter(user=user)

    return query.exists()

# def check_if_participant_is_wearing_fitbit(fitbit_account):
#     fitbit_days = 


@shared_task
def fitbit_update_check(username):
    user = User.objects.get(username=username)
    
    if raise_exceptions_if_inappropriate(user):
        # Fitbit update check
        fitbit_account = get_fitbit_account(user)

        last_update = fitbit_account.last_updated
        if not last_update:
            EventLog.error(user, "No device update record. Notifying user to contact study staff.")
            msg = "[JustWalk] Your Fitbit account seems like not to be connected to your study account. Please contact the study staff. Email: justwalk@ucsd.edu [Code:0001]"
            sms_service = SMSService(user=user)
            sms_message = sms_service.send(msg)
            send_mail_to_justwalk_staff(
                '[JustWalk-0001] No Fitbit account error [{}]'.format(username),
                'Participant ID: {}\nFitbit account seems not to be connected to their study account. The participant is notified through the text.'.format(username),
                'staff'
            )
        else:
            # There is at least one Fitbit update
            MAXIMUM_FITBIT_UPDATE_DELAY = datetime.timedelta(minutes=60)

            diff = get_time_gap_since_last_update(last_update)
            
            if diff > MAXIMUM_FITBIT_UPDATE_DELAY:
                EventLog.info(user, "Latest Fitbit Update is older than {}. SMS message should be sent.".format(MAXIMUM_FITBIT_UPDATE_DELAY))
                
                greeting = get_greeting(user)
                timegap_str = get_timegap_string(diff)

                msg = "[JustWalk] {}It's been {} since the last data was uploaded. Please launch the Fitbit app to upload. [Code:0002]".format(greeting, timegap_str)

                sms_service = SMSService(user=user)
                sms_message = sms_service.send(msg)
                EventLog.info(user, "SMS message is sent: {}".format(msg))
                EventLog.info(user, "SMS message is sent: {}".format(sms_message.__dict__))
            else:
                EventLog.info(user, "Recent Fitbit Update Exists. No SMS message should be sent.")
        
        # send daily step goal notification
        if FeatureFlags.has_flag(user, "system_id_stepgoal"):
            send_daily_step_goal_notification(username)
        
        # check if the participant has device logged in
        if not check_if_device_connected(user):
            msg = 'Participant ID: {}\nThe participant seems like they deleted the app or unsubscribed from the notifications. Please contact the participant. The participant is not notified in any way.'.format(username)
            EventLog.info(user, msg)
            send_mail_to_justwalk_staff(
                '[JustWalk-0003] No App installed error [{}]'.format(username),
                msg,
                'staff'
            )

        # # check if the participant is not wearing the fitbit for more than 3 days
        # if not check_if_participant_is_wearing_fitbit(fitbit_account):
        #     admin_msg = 'Participant ID: {}\nThe participant seems like they are not wearing the fitbit for more than 3 days. The participant is notified via text.'.format(username)
        #     participant_msg = "[JustWalk] Hi, my name is Junghwan Park. According to our database, it seems like you have not wearing the Fitbit for three days. We're just checking in to see if we can help, such as work out any technical issues. Can you let us know whats going on how we might be able to help? Email: justwalk@ucsd.edu [Code: 0004]"

        #     EventLog.info(user, admin_msg)
        #     sms_service = SMSService(user=user)
        #     sms_message = sms_service.send(participant_msg)

        #     send_mail_to_justwalk_staff(
        #         '[JustWalk-0004] Not wearing Fitbit for 3 days [{}]'.format(username),
        #         admin_msg,
        #         'staff'
        #     )

    else:
        # it is not inappropriate, but there's nothing to do. just do nothing
        pass

def get_timegap_string(diff):
    if diff > datetime.timedelta(hours=36):
        timegap_str = "a while"
    elif diff > datetime.timedelta(hours=12):
        timegap_str = "a day"
    elif diff > datetime.timedelta(minutes=90):
        timegap_str = "a few hours"
    else:
        timegap_str = "a while"
    return timegap_str

def get_greeting(user):
    local_time = get_local_time_by_user(user)
    if local_time.hour < 12 and local_time.hour > 3:
        greeting = "Good morning! "
    elif local_time.hour < 16 and local_time.hour >= 12:
        greeting = "Good afternoon. "
    elif local_time.hour < 22 and local_time.hour >= 16:
        greeting = "Good evening. "
    else:
        greeting = ""
    return greeting

def get_local_time_by_user(user):
    day_service = DayService(user)
    local_time = day_service.get_current_datetime()
    return local_time

def get_time_gap_since_last_update(last_update):
    now = datetime.datetime.now().astimezone(pytz.utc)
    diff = now - last_update
    return diff