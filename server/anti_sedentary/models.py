from django.db import models

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision

class AntiSedentaryDecision(Decision):
    pass

class AntiSedentaryMessageTemplate(MessageTemplate):
    pass
