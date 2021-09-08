from user_event_logs.models import EventLog
from push_messages.services import PushMessageService

from .models import Level, RandomDecision, BoutPlanningDecision

class BoutPlanningNotificationService:
    class NotificationSendError(RuntimeError):
        pass

    def __init__(self, user):
        assert user is not None, "User must be specified"

        self.user = user
        EventLog.debug(self.user, "Starting BoutPlanningNotificationService")

    def is_necessary(self):
        EventLog.debug(self.user, "is_necessary() is called")
        
        level = Level.get(self.user)
        
        if level.level == Level.RECOVERY:
            return_bool = False
        elif level.level == Level.RANDOM:
            decision = RandomDecision.create(self.user)
            return_bool = decision.decide()
        elif level.level == Level.NO:
            decision = BoutPlanningDecision.create(self.user)
            decision.apply_N()
            decision.apply_O()
            return_bool = decision.decide()
        elif level.level == Level.NR:
            decision = BoutPlanningDecision.create(self.user)
            decision.apply_N()
            decision.apply_R()
            return_bool = decision.decide()
        elif level.level == Level.FULL:
            decision = BoutPlanningDecision.create(self.user)
            decision.apply_N()
            decision.apply_O()
            decision.apply_R()
            return_bool = decision.decide()
        else:
            raise RuntimeError("Unsupported decision type: {}".format(level.level))
        
        EventLog.debug(self.user, "returning True")
        return return_bool
    
    def send_notification(self,
                          title='Sample Bout Planning Title',
                          body='Sample Bout Planning Body.',
                          collapse_subject='bout_planninng',
                          data={}):
        try:
            service = PushMessageService(user=self.user)
            message = service.send_notification(
                body=body,
                title=title,
                collapse_subject=collapse_subject,
                data=data)
            return message
        except (PushMessageService.MessageSendError,
                PushMessageService.DeviceMissingError) as e:
            raise BoutPlanningNotificationService.NotificationSendError(
                'Unable to send notification')
