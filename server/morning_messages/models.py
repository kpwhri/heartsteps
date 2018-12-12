from django.db import models

from behavioral_messages.models import MessageTemplate, ContextTag
from randomization.models import Decision

class MorningMessageTemplate(MessageTemplate):
    anchor_message = models.CharField(max_length=255)

class MorningMessageDecision(Decision):
    pass
