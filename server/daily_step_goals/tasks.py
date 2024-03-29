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
from days.services import DayService



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
            collapse_subject=collapse_subject,
            data=data)
        return message
    except (PushMessageService.MessageSendError,
            PushMessageService.DeviceMissingError) as e:
        raise e
        
@shared_task
def send_daily_step_goal_notification(username, parameters=None):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)
    
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

        message = send_notification(user, title="JustWalk", body="Today's step goal: {:,}".format(goal), collapse_subject="bout_planning_survey", survey=survey)
    else:
        EventLog.info(user, "The user is not yet baseline complete. The daily step goal notification will not be sent.")
        return
            
    


@shared_task
def update_goal(username, day=None):
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    
    user = User.objects.get(username=username)
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
        EventLog.debug(user, "The user is not in baseline period. moving on.")
        pass
    else:
        # The user is in baseline period. Stopping here.
        EventLog.info(user, "The user is in baseline period. Setting the goal to 10,000 steps per day, and stopping here.")
        BASELINE_STEPGOAL = 2000
        set_fixed_goal(user, day, BASELINE_STEPGOAL)
        return

    EventLog.debug(user, "StepGoalsService is being created.")
    stepgoal_service = daily_step_goals.services.StepGoalsService(user)
    EventLog.debug(user, "StepGoalsService is created.")
    query = StepGoalsEvidence.objects.filter(user=user, startdate__lte=day, enddate__gte=day).order_by('-created')
    
    if not query.exists():
        EventLog.info(user, "No evidence found for today.")
        # no calculation evidence is found
        last_evidence_query = StepGoalsEvidence.objects.filter(user=user).order_by('-enddate', '-created')
        if not last_evidence_query.exists():
            EventLog.debug(user, "No evidence found for any day.")
            # no evidence is found at all
            startdate = day
        else:
            EventLog.debug(user, "some evidence is found")
            # some evidence is found
            last_evidence = last_evidence_query.first()
            if last_evidence.enddate > day:
                EventLog.debug(user, "The last evidence is for the future. calculation is completely wrong")
                # calculation is completely wrong. re-calculating from the start
                # startdate = enrollment_date + timedelta(days=baseline_period)
                raise Exception("The last evidence is for the future. calculation is completely wrong")
            else:
                EventLog.debug(user, "The last evidence is for the past. calculation is somewhat correct. setting the startdate to the last evidence's enddate + 1d")
                # calculation stopped sometime before
                startdate = last_evidence.enddate + timedelta(days=1)            
        
        EventLog.debug(user, "Getting into the loop: Calculating the goal for the day.")
        while startdate <= day:
            EventLog.debug(user, "Calculating the goal for the day: startdate={}".format(startdate))
            evidence = stepgoal_service.calculate_step_goals(startdate=startdate)
            EventLog.debug(user, "Finished the calculation: evidence={}".format(evidence))
            startdate = evidence.enddate + timedelta(days=1)
        EventLog.debug(user, "Finished the loop: Calculating the goal for the day.")
    else:
        EventLog.debug(user, "The evidence for today is found.")
        # this query is called repeatedly even there is an evidence that covers today.
        # recalculating and if it doesn't match with the previous records, we keep history.
        evidence_for_today = query.first()
        startdate = evidence_for_today.startdate
        EventLog.debug(user, "Doing a single calculation: Calculating the goal for the day.")
        stepgoal_service.calculate_step_goals(startdate=startdate)
        EventLog.debug(user, "Finished the calculation: evidence={}".format(evidence_for_today))
    EventLog.debug(user, "Finished the loop: Fetching the goal for the day.")
    step_goal = stepgoal_service.get_goal(day)
    EventLog.debug(user, "Today's goal: {}".format(step_goal))
    
    EventLog.debug(user, "Setting the goal for the day to the fitbit.")
    update_fitbit_device_with_new_goal(user, step_goal)
    EventLog.debug(user, "Finished the goal setting for the day to the fitbit.")

def set_fixed_goal(user, day, BASELINE_STEPGOAL):
    if StepGoal.objects.filter(user=user, date=day).exists():
        goal_obj = StepGoal.get(user=user, date=day)
        goal_obj.step_goal = BASELINE_STEPGOAL
        goal_obj.save()
    else:
        StepGoal.objects.create(user=user, date=day, step_goal=BASELINE_STEPGOAL)
            
    update_fitbit_device_with_new_goal(user, BASELINE_STEPGOAL)

def update_fitbit_device_with_new_goal(user, step_goal):
    fitbit_service = fitbit_api.services.FitbitClient(user)
    
    fitbit_service.update_step_goals(step_goal)
