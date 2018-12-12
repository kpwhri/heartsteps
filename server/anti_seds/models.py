from django.db import models
from django.contrib.auth.models import User

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision

class AntiSedentaryDecision(Decision):
    pass

class AntiSedentaryMessageTemplate(MessageTemplate):
    pass

class StepCount(models.Model):
    user = models.ForeignKey(User)
    step_number = models.IntegerField(null=True, blank=True)
    step_dtm = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s steps %s @ %s" % (self.user, self.step_number, self.step_dtm)
