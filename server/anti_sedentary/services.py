
from django.utils import timezone

from randomization.services import DecisionMessageService

from anti_sedentary.models import AntiSedentaryDecision, AntiSedentaryMessageTemplate

class AntiSedentaryDecisionService(DecisionMessageService):

    MESSAGE_TEMPLATE_MODEL = AntiSedentaryMessageTemplate

    def create_decision(user, test=False):
        decision = AntiSedentaryDecision.objects.create(
            user = user,
            test = test,
            time = timezone.now()
        )
        return AntiSedentaryDecisionService(decision)