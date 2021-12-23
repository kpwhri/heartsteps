from days.services import DayService
from surveys.serializers import SurveySerializer, SurveyShirinker
from user_event_logs.models import EventLog
from push_messages.services import PushMessageService

from .models import BoutPlanningSurvey, Level, BoutPlanningDecision, BoutPlanningNotification, JustWalkJitaiDailyEma

class BoutPlanningNotificationService:
    class NotificationSendError(RuntimeError):
        pass

    def __init__(self, user):
        assert user is not None, "User must be specified"

        self.user = user
        self.level = None
        self.decision = None
        EventLog.debug(self.user, "Starting BoutPlanningNotificationService")

    def create_survey(self):
        bout_planning_survey = BoutPlanningSurvey.objects.create(user=self.user)
        bout_planning_survey.reset_questions()
        
        return bout_planning_survey
    
    def create_test_survey(self):
        return self.create_survey()
    
    def create_daily_ema(self):
        daily_ema_survey = JustWalkJitaiDailyEma.objects.create(user=self.user)
        daily_ema_survey.reset_questions()
        
        return daily_ema_survey
    
    
    def is_necessary(self):
        EventLog.debug(self.user, "is_necessary() is called")
        self.decision = BoutPlanningDecision.create(self.user)
        self.decision.add_line("BoutPlanningDecision object is created")
        
        day_service = DayService(self.user)
        
        self.decision.add_line("Starting is_necessary() calculation for {} @ {} (local)".format(self.user.username, day_service.get_current_datetime()))
        self.level = Level.get(self.user)
        self.decision.data["level"] = str(self.level.level)
        self.decision.add_line("Level '{}' is fetched from DB".format(self.level))
        
        if self.level.level == Level.RECOVERY:
            self.decision.add_line("Since the level is RECOVERY, no further processing is done.")
            return_bool = False
        elif self.level.level == Level.RANDOM:
            self.decision.add_line("Since the level is RANDOM, apply_random is done.")
            self.decision.apply_random()
            return_bool = self.decision.decide()
        elif self.level.level == Level.NO:
            self.decision.add_line("Since the level is NO, apply_N and apply_O are done.")
            self.decision.apply_N()
            self.decision.apply_O()
            return_bool = self.decision.decide()
        elif self.level.level == Level.NR:
            self.decision.add_line("Since the level is NR, apply_N and apply_R are done.")
            self.decision.apply_N()
            self.decision.apply_R()
            return_bool = self.decision.decide()
        elif self.level.level == Level.FULL:
            self.decision.add_line("Since the level is FULL, apply_N, apply_O, and apply_R are done.")
            self.decision.apply_N()
            self.decision.apply_O()
            self.decision.apply_R()
            return_bool = self.decision.decide()
        else:
            raise RuntimeError("Unsupported decision type: {}".format(self.level.level))
        self.decision.add_line("The decision is delivered: {}".format(return_bool))
        self.decision.save()
        return return_bool
    
    def send_notification(self,
                          title='Sample Bout Planning Title',
                          body='Sample Bout Planning Body.',
                          collapse_subject='bout_planninng',
                          survey=None,
                          data={}):
        try:
            EventLog.debug(self.user, "BoutPlanningNotificationService.send_notification()")
            if survey is not None:
                EventLog.debug(self.user, "BoutPlanningNotificationService.send_notification() - survey is not None")
                shrinked_survey = SurveyShirinker(survey)
                EventLog.debug(self.user, "BoutPlanningNotificationService.send_notification() - Survey is shrinked")
                data["survey"] = shrinked_survey.to_json()
                EventLog.debug(self.user, "{}".format(shrinked_survey.to_json()))
            
            service = PushMessageService(user=self.user)
            EventLog.debug(self.user)
            message = service.send_notification(
                body=body,
                title=title,
                collapse_subject=collapse_subject,
                data=data)
            EventLog.debug(self.user)
            BoutPlanningNotification.create(user=self.user, message=message, level=self.level, decision=self.decision)
            EventLog.debug(self.user)
            return message
        except (PushMessageService.MessageSendError,
                PushMessageService.DeviceMissingError) as e:
            raise BoutPlanningNotificationService.NotificationSendError(
                'Unable to send notification')
