from django.db import models
from django.contrib.auth import get_user_model

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision
from service_requests.models import ServiceRequest

User = get_user_model()

class Configuration(models.Model):
    user = models.ForeignKey(User, related_name="anti_sedentary_configuration")
    enabled = models.BooleanField(default=False)

    def __str__(self):
        if self.enabled:
            return self.user.username + ' (enabled)'
        else:
            return self.user.username + ' (disabled)'

class AntiSedentaryMessageTemplate(MessageTemplate):
    pass

class AntiSedentaryServiceRequest(ServiceRequest):
    pass

class AntiSedentaryDecision(Decision):
    MESSAGE_TEMPLATE_MODEL = AntiSedentaryMessageTemplate

    sedentary = models.NullBooleanField(null=True)

    def get_treatment_probability(self):
        return 0.15
