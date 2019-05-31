from datetime import datetime, date

from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from days.services import DayService
from push_messages.services import PushMessageService
from randomization.services import DecisionMessageService

from .models import Configuration, MorningMessage, MorningMessageDecision, MorningMessageTemplate
from .serializers import MorningMessageSerializer

class MorningMessageService:

    class NotConfigured(ImproperlyConfigured):
        pass

    class NotEnabled(ImproperlyConfigured):
        pass

    class MessageDoesNotExist(MorningMessage.DoesNotExist):
        pass

    def __init__(self, configuration=None, user=None, username=None):
        if configuration:
            self.__configuration = configuration
        else:
            try:
                if username:
                    self.__configuration = Configuration.objects.get(user__username=username)
                elif user:
                    self.__configuration = Configuration.objects.get(user=user)
                else:
                    raise Configuration.DoesNotExist()
            except Configuration.DoesNotExist:
                raise self.NotConfigured()

        self.__user = self.__configuration.user

    def get_or_create(self, date):
        try:
            return (self.get(date), False)
        except MorningMessageService.MessageDoesNotExist:
            return (self.create(date), True)

    def get(self, date):
        try:
            return MorningMessage.objects.get(
                user = self.__user,
                date__year = date.year,
                date__month = date.month,
                date__day = date.day
            )
        except MorningMessage.DoesNotExist:
            raise MorningMessageService.MessageDoesNotExist()

    def create(self, date, message_framing=False):
        morning_message = MorningMessage.objects.create(
            user = self.__user,
            date = date,
            message_decision = self.create_message_decision(date)
        )
        return morning_message

    def create_message_decision(self, date):
        morning_message_decision = MorningMessageDecision.objects.create(
            user = self.__user,
            treated = True,
            treatment_probability = 1,
            available = True,
            time = self.get_message_decision_time(date)
        )
        morning_message_decision.set_message_frame()
        return morning_message_decision 

    def get_message_decision_time(self, date):
        service = DayService(user=self.__user)
        timezone = service.get_timezone_at(date)
        return timezone.localize(datetime(date.year, date.month, date.day, 6, 0))

    
    def update_message(self, date, message_framing=False):
        morning_message, _ = self.get_or_create(date)
        morning_message.message_decision.set_message_frame(message_framing)
        morning_message.save()

    def send_notification(self, day=False, test=False):
        if not day:
            service = DayService(user=self.__user)
            day = service.get_current_date()
        morning_message, _ = self.get_or_create(day)

        if not self.__configuration.enabled:
            raise MorningMessageService.NotEnabled()

        serialized = MorningMessageSerializer(morning_message).data
        serialized['type'] = 'morning-message'

        if not serialized['text']:
            del serialized['text']
        if not serialized['anchor']:
            del serialized['anchor']
        
        if serialized['notification']:
            serialized['body'] = serialized['notification']
            del serialized['notification']

        push_service = PushMessageService(user=self.__user)
        message = push_service.send_notification(
            body = morning_message.notification,
            title = 'Morning message',
            data = serialized
        )
        morning_message.add_context(message)

class MorningMessageDecisionService(DecisionMessageService):

    class NotConfigured(ImproperlyConfigured):
        pass

    class NotEnabled(ImproperlyConfigured):
        pass

    MESSAGE_TEMPLATE_MODEL = MorningMessageTemplate

    def get_message_template(self):
        if self.decision.get_message_frame():
            return super(MorningMessageDecisionService, self).get_message_template()
        else:
            class DefaultMessageTemplate:
                body = "Good Morning"
                title = "Good Morning"
            return DefaultMessageTemplate()
