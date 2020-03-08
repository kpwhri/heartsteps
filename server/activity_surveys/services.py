from push_messages.services import PushMessageService
from surveys.serializers import SurveySerializer

from .models import ActivitySurvey
from .models import Configuration
from .models import User

class ActivitySurveyService:

    class NotConfigured(RuntimeError):
        pass
    
    class NotificationSendError(RuntimeError):
        pass

    def __init__(self, configuration=None, user=None, username=None):
        try:
            if username:
                configuration = Configuration.objects.get(user__username=username)
            if user:
                configuration = Configuration.objects.get(user=user)
        except Configuration.DoesNotExist:
            pass
        if configuration:
            self.configuration = configuration
        else:
            raise ActivitySurveyService.NotConfigured('No configuration')
        

    def create_survey(self, fitbit_activity=None):
        activity_survey = ActivitySurvey.objects.create(
            user = self.configuration.user
        )
        activity_survey.reset_questions()
        return activity_survey

    def create_test_survey(self):
        return self.create_survey()

    def send_notification(self, activity_survey):
        serialized_survey = SurveySerializer(activity_survey)
        try:
            service = PushMessageService(user = self.configuration.user)
            message = service.send_notification(
                body = 'Tell us about the activity you just completed.',
                title = 'Activity Survey',
                collapse_subject = 'activity_survey',
                data = {
                    'survey':serialized_survey.data
                }
            )
            return message
        except (PushMessageService.MessageSendError, PushMessageService.DeviceMissingError) as e:
            raise ActivitySurveyService.NotificationSendError('Unable to send notification')
                
