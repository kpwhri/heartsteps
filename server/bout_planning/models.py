import uuid
from django.db import models
from django.contrib.auth import get_user_model

from behavioral_messages.models import MessageTemplate
from randomization.models import Decision
from randomization.models import DecisionContextQuerySet
from service_requests.models import ServiceRequest

User = get_user_model()

class BoutPlanningConfiguration(models.Model):
    user = models.ForeignKey(User, related_name="bout_planning_configuration", on_delete = models.CASCADE)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        if self.enabled:
            return self.user.username + ' (enabled)'
        else:
            return self.user.username + ' (disabled)'

class GenericMessageModel(models.Model):
    parent_id = models.CharField(max_length=100, null=True)     # easy, short name for the project
    message_id = models.CharField(max_length=100, null=True)    # period-delimited long name for the message
    message_title = models.TextField(null=True)
    message_body = models.TextField(null=True)
    
    class Meta:
        unique_together = ['parent_id', 'message_id']

class GenericMessageSentLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message_template = models.ForeignKey(GenericMessageModel, null=False, on_delete=models.CASCADE)