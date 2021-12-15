from surveys.serializers import SurveySerializer
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
        
        self.level = Level.get(self.user)
        
        if self.level.level == Level.RECOVERY:
            return_bool = False
        elif self.level.level == Level.RANDOM:
            self.decision = BoutPlanningDecision.create(self.user)
            self.decision.apply_random()
            return_bool = self.decision.decide()
        elif self.level.level == Level.NO:
            self.decision = BoutPlanningDecision.create(self.user)
            self.decision.apply_N()
            self.decision.apply_O()
            return_bool = self.decision.decide()
        elif self.level.level == Level.NR:
            self.decision = BoutPlanningDecision.create(self.user)
            self.decision.apply_N()
            self.decision.apply_R()
            return_bool = self.decision.decide()
        elif self.level.level == Level.FULL:
            self.decision = BoutPlanningDecision.create(self.user)
            self.decision.apply_N()
            self.decision.apply_O()
            self.decision.apply_R()
            return_bool = self.decision.decide()
        else:
            raise RuntimeError("Unsupported decision type: {}".format(self.level.level))
        
        EventLog.debug(self.user, "returning True")
        return return_bool
    
    def send_notification(self,
                          title='Sample Bout Planning Title',
                          body='Sample Bout Planning Body.',
                          collapse_subject='bout_planninng',
                          survey=None,
                          data={}):
        try:
            if survey is not None:
                serialized_survey = SurveySerializer(survey)
                print(serialized_survey.data)
                data["survey"] = serialized_survey.data
                
            service = PushMessageService(user=self.user)
            message = service.send_notification(
                body=body,
                title=title,
                collapse_subject=collapse_subject,
                data=data)
            BoutPlanningNotification.create(user=self.user, message=message, level=self.level, decision=self.decision)
            return message
        except (PushMessageService.MessageSendError,
                PushMessageService.DeviceMissingError) as e:
            raise BoutPlanningNotificationService.NotificationSendError(
                'Unable to send notification')
