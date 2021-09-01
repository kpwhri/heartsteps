from user_event_logs.models import EventLog
from push_messages.services import PushMessageService


class BoutPlanningNotificationService:
    class NotificationSendError(RuntimeError):
        pass

    def __init__(self, user):
        assert user is not None, "User must be specified"

        self.user = user
        EventLog.debug(self.user, "Starting BoutPlanningNotificationService")

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
