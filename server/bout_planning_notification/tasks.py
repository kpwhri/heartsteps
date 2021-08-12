from celery import shared_task
from .models import User
from user_event_logs.models import EventLog
from feature_flags.models import FeatureFlags

class BoutPlanningFlagException(Exception):
    pass

@shared_task
def bout_planning_decision_making(username):
    """Main logic for bout planning decision making. This runs every three hours
    task id: bout_planning_notification.tasks.bout_planning_decision_making
    """
    assert isinstance(username, str), "username must be a string: {}".format(type(username))
    user = User.objects.get(username=username)

    if FeatureFlags.exists(user):
        if FeatureFlags.has_flag(user, "bout_planning"):
            # do something
            EventLog.log(user, "bout planning shared_task has run", EventLog.INFO)
        else:
            msg = "a user without 'bout_planning' flag came into bout_planning_decision_making"
            EventLog.log(user, msg, EventLog.ERROR)
            raise BoutPlanningFlagException(msg)
    else:
        msg = "a user without any flag came into bout_planning_decision_making"
        EventLog.log(user, msg, EventLog.ERROR)
        raise BoutPlanningFlagException(msg)