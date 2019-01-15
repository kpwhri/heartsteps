from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from randomization.services import DecisionMessageService

from .models import Configuration, MorningMessageDecision, MorningMessageTemplate

class MorningMessageService:

    class MessageDoesNotExist(MorningMessageDecision.DoesNotExist):
        pass

    def __init__(self, user):
        self.__user = user

    def get_message_on(self, date):
        try:
            decision = MorningMessageDecision.objects.get(
                user = self.__user,
                time__year = date.year,
                time__month = date.month,
                time__day = date.day
            )
        except MorningMessageDecision.DoesNotExist:
            raise MorningMessageService.MessageDoesNotExist()
        return decision.notification
        

    

class MorningMessageDecisionService(DecisionMessageService):

    class NotConfigured(ImproperlyConfigured):
        pass

    class NotEnabled(ImproperlyConfigured):
        pass

    MESSAGE_TEMPLATE_MODEL = MorningMessageTemplate

    def __init__(self, decision=None, user=None, username=None):
        try:
            if username:
                self.configuration = Configuration.objects.get(user__username=username)
            elif user:
                self.configuration = Configuration.objects.get(user=user)
            else:
                raise Configuration.DoesNotExist()
        except Configuration.DoesNotExist:
            raise self.NotConfigured()

        self.user = self.configuration.user
        self.decision = decision

    def get_message_template(self):
        if self.decision.get_message_frame():
            return super(MorningMessageDecisionService, self).get_message_template()
        else:
            class DefaultMessageTemplate:
                body = "Good Morning"
                title = "Good Morning"
            return DefaultMessageTemplate()

    def send_message(self):
        if not self.configuration.enabled:
            raise self.NotEnabled()
        if not self.decision:
            self.decision = MorningMessageDecision.objects.create(
                user = self.user,
                time = timezone.now()
            )
        super(MorningMessageDecisionService, self).send_message()
