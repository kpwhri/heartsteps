from django.db import models
from django.contrib.auth import get_user_model

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision

User = get_user_model()

class AntiSedentaryDecision(Decision):
    pass

class AntiSedentaryMessageTemplate(MessageTemplate):
    pass
