from django.db import models
from django.contrib.auth import get_user_model

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision

User = get_user_model()

class AntiSedentaryDecision(Decision):

    def get_treatment_probability(self):
        return 0.15

class AntiSedentaryMessageTemplate(MessageTemplate):
    pass
