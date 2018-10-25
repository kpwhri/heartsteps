import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from push_messages.models import Message as PushMessage
from push_messages.services import PushMessageService

class ContextTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=25)

    name = models.CharField(max_length=50, null=True, blank=True)
    dashboard = models.BooleanField(default=False)

    def __str__(self):
        return self.name or self.tag

class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    time = models.DateTimeField()

    a_it = models.NullBooleanField(null=True, blank=True)
    pi_it = models.FloatField(null=True, blank=True)

    tags = models.ManyToManyField(ContextTag)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_complete(self):
        if self.a_it is not None:
            return True
        else:
            return False

    def __str__(self):
        if self.a_it is None:
            return "For %s (undecided)" % self.user
        else:
            return "For %s (decided)" % self.user

class DecisionContext(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.ForeignKey(Decision)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.OneToOneField(Decision)

    message_template = models.ForeignKey(MessageTemplate)
    sent_message = models.OneToOneField(PushMessage, null=True, blank=True, related_name="randomization_message")
