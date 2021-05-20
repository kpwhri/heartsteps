from datetime import date
from datetime import datetime
from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from days.services import DayService
# from fitbit_activities.services import FitbitStepCountService
# from fitbit_api.services import FitbitService
from randomization.services import DecisionContextService
from randomization.services import DecisionMessageService
from randomization.models import ContextTag
from walking_suggestion_times.models import SuggestionTime
from watch_app.services import StepCountService

from push_messages.services import PushMessageService
from .models import BoutPlanningConfiguration
from .models import GenericMessageModel, GenericMessageSentLog

class BoutPlanningService:

    class Unavailable(ImproperlyConfigured):
        pass

    class NoConfiguration(ImproperlyConfigured):
        """Unable to fetch configuration. Usually it's the case that we cannot bring user object.
        """
        pass
    
    class NoSteps(ValueError):
        pass
    
    class RequestError(RuntimeError):
        pass

    def __init__(self, configuration=None, username=None):
        try:
            if username:
                configuration = BoutPlanningConfiguration.objects.get(user__username=username) 
        except BoutPlanningConfiguration.DoesNotExist:
            pass
        if not configuration:
            raise BoutPlanningService.NoConfiguration('No configuration: configuration={}, username={}'.format(configuration, username))
        
        self.__configuration = configuration
        self.__user = configuration.user

    def create_service(username=None):
        return BoutPlanningService(username=username)


    def create_message_template(self, parent_id: str, message_id: str, message_title: str, message_body: str):
        message_template, isCreated = GenericMessageModel.objects.get_or_create(
            parent_id = parent_id,
            message_id = message_id
        )
        
        if isCreated:
            message_template.message_title = message_title
            message_template.message_body = message_body
            message_template.save()
        else:
            if message_template.message_title == message_title:
                pass
            else:
                raise ValueError("This messageId is used before: message_title={}, message_body={}".format(message_template.message_title, message_template.message_body))
        
        return message_template

    def get_message_template(self, parent_id: str, message_id: str, message_title: str, message_body: str):
        if hasattr(self, '__message_template'):
            # reuse previous message template
            return self.__message_template
        else:
            message_template = self.create_message_template(parent_id, message_id, message_title, message_body)
            self.__message_template = message_template
            return message_template
            
    def issue_sent_log(self, message_template: GenericMessageModel):
        sent_log = GenericMessageSentLog.objects.create(message_template=message_template)
        return sent_log
        
    def send_message(self, parent_id: str, message_id: str, message_title: str, message_body: str, is_test:bool=False):
        push_message_service = PushMessageService(self.__user)
        
        if is_test:
            message_template = self.get_message_template("test", "test", "Hello", "HeartSteps!")
        else:
            message_template = self.get_message_template(parent_id, message_id, message_title, message_body)
        
        self.sent_log = self.issue_sent_log(message_template)
        
        message = push_message_service.send_notification(
            message_template.message_body,
            title = message_template.message_title,
            data = {
                'randomizationId': str(self.sent_log.id)
            },
            collapse_subject = 'generic-message'
        )
        return message
        
    def enable(self):
        if not self.__configuration.enabled:
            self.__configuration.enabled = True
            self.__configuration.save()

    def update(self, date):
        if not self._client:
            raise BoutPlanningService.Unavailable('No client')