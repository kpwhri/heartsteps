from datetime import timedelta

from django.utils import timezone

from push_messages.services import PushMessageService
from surveys.serializers import SurveySerializer

from .models import ActivitySurvey
from .models import Configuration
from .models import Decision
from .models import User

class ActivitySurveyService:

    class NotConfigured(RuntimeError):
        pass
    
    class NotificationSendError(RuntimeError):
        pass
    
    class SurveyNotRandomized(RuntimeError):
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
            self.user = configuration.user
        else:
            raise ActivitySurveyService.NotConfigured('No configuration')

    def randomize_survey(self, fitbit_activity=None, treatment_probability=None):
        if not treatment_probability:
            treatment_probability = self.configuration.treatment_probability
        decision = Decision(
            user = self.user,
            treatment_probability = treatment_probability
        )
        if not self.configuration.enabled:
            decision.treatment_probability = 0
        hour_ago = timezone.now() - timedelta(minutes=60)
        if fitbit_activity and fitbit_activity.end_time < hour_ago:
            decision.treatment_probability = 0
        decision.randomize()
        decision.save()
        if decision.treated:
            decision.survey = self.create_survey(
                decision = decision,
                fitbit_activity = fitbit_activity
            )
            decision.notification = self.send_notification(decision.survey)
        decision.save()

    def create_survey(self, decision=None, fitbit_activity=None):
        activity_survey = ActivitySurvey.objects.create(
            user = self.configuration.user,
            decision = decision,
            fitbit_activity = fitbit_activity
        )
        if decision:
            decision.activity_survey = activity_survey
            decision.fitbit_activity = fitbit_activity
            decision.save()
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
                
