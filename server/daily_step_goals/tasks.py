import requests
import datetime
from participants.models import Participant
from celery import shared_task
from datetime import timedelta
from daily_step_goals.models import StepGoalsEvidence, User
import participants
from daily_step_goals.models import StepGoal
from feature_flags.models import FeatureFlags
import bout_planning_notification as bpn
from participants.services import ParticipantService
from push_messages.services import PushMessageService
from surveys.serializers import SurveyShirinker
from user_event_logs.models import EventLog

import daily_step_goals.services
import fitbit_api.services
import fitbit_api.models
from days.services import DayService


def get_collapse_subject(prefix):
    return "{}_{}".format(prefix, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))


def send_notification(user, title='Sample Stepgoal Notification Title',
                        body='Sample Stepgoal Notification Body.',
                        collapse_subject='stepgoal',
                        survey=None,
                        data={}):
    try:
        if survey is not None:
            shrinked_survey = SurveyShirinker(survey)
            data["survey"] = shrinked_survey.to_json()
        
        service = PushMessageService(user=user)
        message = service.send_notification(
            body=body,
            title=title,
            collapse_subject=get_collapse_subject('stepgoal'),
            data=data)
        return message
    except (PushMessageService.MessageSendError,
            PushMessageService.DeviceMissingError) as e:
        raise e
        
@shared_task
def send_daily_step_goal_notification(username, parameters=None):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)
    
    if user.is_active:
        if not FeatureFlags.exists(user):
            raise Exception("The user does not have a feature flag.")
        
        if not FeatureFlags.has_flag(user, "system_id_stepgoal"):
            raise Exception("The user does not have 'system_id_stepgoal' flag.")
        
        participant_service = ParticipantService(user=user)
        if participant_service.is_baseline_complete():
            day_service = DayService(user)
            today = day_service.get_current_date()

            goal = StepGoal.get(user=user, date=today)
            # goal_query = StepGoal.get(user=user, date=today)
            # if goal_query.exists():
            #     goal = goal_query.first().step_goal
            # else:
            #     raise Exception("No goal found for today.")

            json_survey = bpn.models.JSONSurvey.objects.get(name="daily_goal_survey")
            survey = json_survey.substantiate(user, parameters)

            message = send_notification(user, title="JustWalk", body="Today's step goal: {:,}".format(goal), collapse_subject=get_collapse_subject('dsg1'), survey=survey)
        else:
            EventLog.info(user, "The user is not yet baseline complete. The daily step goal notification will not be sent.")
            return
    else:
        EventLog.info(user, "[send_daily_step_goal_notification] The user is not active.")
    


@shared_task
def update_goal(username, day=None):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    
    user = User.objects.get(username=username)
    EventLog.info(user, "[update_goal] update_goal() launched")
    if user.is_active:
        EventLog.info(user, "[update_goal] user.is_active")
        participant = Participant.objects.get(user=user)
        enrollment_date = participant.study_start_date
        day_service = DayService(user)
        today = day_service.get_current_date()
        if day is None:
            day = today

        # Checking if the user is in baseline period or not"
        participant_service = participants.services.ParticipantService(user=user)
        if participant_service.is_baseline_complete():
            # The user is not in baseline period. moving on.
            EventLog.info(user, "[update_goal] participant_service.is_baseline_complete()")
            pass
        else:
            # The user is in baseline period. Stopping here.
            EventLog.info(user, "[update_goal] not participant_service.is_baseline_complete()")
            EventLog.info(user, "The user is in baseline period. Setting the goal to 10,000 steps per day, and stopping here.")
            BASELINE_STEPGOAL = 2000
            set_fixed_goal(user, day, BASELINE_STEPGOAL)
            return

        stepgoal_service = daily_step_goals.services.StepGoalsService(user)
        query = StepGoalsEvidence.objects.filter(user=user, startdate__lte=day, enddate__gte=day).order_by('-created')
        
        if not query.exists():
            EventLog.info(user, "[update_goal] not query.exists()")
            EventLog.info(user, "No evidence found for today.")
            # no calculation evidence is found
            last_evidence_query = StepGoalsEvidence.objects.filter(user=user).order_by('-enddate', '-created')
            if not last_evidence_query.exists():
                # no evidence is found at all
                EventLog.info(user, "[update_goal] not last_evidence_query.exists()")
                startdate = day
            else:
                # some evidence is found
                EventLog.info(user, "[update_goal] last_evidence_query.exists()")
                last_evidence = last_evidence_query.first()
                if last_evidence.enddate > day:
                    # calculation is completely wrong. re-calculating from the start
                    # startdate = enrollment_date + timedelta(days=baseline_period)
                    EventLog.info(user, "[update_goal] last_evidence.enddate > day")
                    raise Exception("The last evidence is for the future. calculation is completely wrong")
                else:
                    # calculation stopped sometime before
                    EventLog.info(user, "[update_goal] not last_evidence.enddate > day")
                    startdate = last_evidence.enddate + timedelta(days=1)            
            
            while startdate <= day:
                EventLog.info(user, "[update_goal] while startdate <= day: startdate={}, day={}".format(startdate, day))
                evidence = stepgoal_service.calculate_step_goals(startdate=startdate)
                startdate = evidence.enddate + timedelta(days=1)
        else:
            # this query is called repeatedly even there is an evidence that covers today.
            # recalculating and if it doesn't match with the previous records, we keep history.
            EventLog.info(user, "[update_goal] query.exists()")
            evidence_for_today = query.first()
            startdate = evidence_for_today.startdate
            stepgoal_service.calculate_step_goals(startdate=startdate)
        EventLog.info(user, "[update_goal] stepgoal_service.get_goal(day): day={}".format(day))
        step_goal = stepgoal_service.get_goal(day)
        EventLog.info(user, "[update_goal] update_fitbit_device_with_new_goal(user, step_goal): step_goal={}".format(step_goal))
        update_fitbit_device_with_new_goal(user, step_goal)
    else:
        EventLog.info(user, "[update_goal] not user.is_active")
    
def set_fixed_goal(user, day, BASELINE_STEPGOAL):
    if StepGoal.objects.filter(user=user, date=day).exists():
        goal_obj = StepGoal.objects.filter(user=user, date=day).order_by('-created').first()
        goal_obj.step_goal = BASELINE_STEPGOAL
        goal_obj.save()
    else:
        StepGoal.objects.create(user=user, date=day, step_goal=BASELINE_STEPGOAL)
            
    update_fitbit_device_with_new_goal(user, BASELINE_STEPGOAL)

# Temporary Goal Update API
def update_fitbit_daily_stepgoal_temporary(user, steps):
    EventLog.info(user, "[update_goal] update_fitbit_daily_stepgoal_temporary() started.")
    fa_service = fitbit_api.services.FitbitClient(user)
    fb_account = fa_service.account
    fb_account_id = fb_account.fitbit_user
    EventLog.info(user, "[update_goal] fa_service.make_request() is prepared.")
    r = fa_service.make_request('user/{}/activities/goals/daily.json?type=steps&value={}'.format(fa_service.account, steps), method='POST')
    EventLog.info(user, "[update_goal] fa_service.make_request() is finished.")
    EventLog.info(user, "[update_goal] r: {}".format(r))

    if 'success' in r and not r['success']:
        EventLog.error(user, "[update_goal] Fitbit request error: {}".format(r))
        raise Exception(r)
    return r

def update_fitbit_device_with_new_goal(user, step_goal):
    # fitbit_service = fitbit_api.services.FitbitClient(user)    
    # fitbit_service.update_step_goals(step_goal)
    EventLog.info(user, "[update_goal] update_fitbit_daily_stepgoal_temporary(user, step_goal) is being called: step_goal={}".format(step_goal))
    update_fitbit_daily_stepgoal_temporary(user, step_goal)
    EventLog.info(user, "[update_goal] update_fitbit_daily_stepgoal_temporary(user, step_goal) is returned: step_goal={}".format(step_goal))