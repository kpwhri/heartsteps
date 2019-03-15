import uuid, random
from datetime import datetime
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.contrib.auth.models import User
from push_messages.models import Message
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

    test = models.BooleanField(default=False)
    imputed = models.BooleanField(default=False)
    
    available = models.BooleanField(default=True)
    unavailable_reason = models.CharField(max_length=150, null=True, blank=True)

    time = models.DateTimeField()

    treated = models.NullBooleanField(null=True, blank=True)
    treatment_probability = models.FloatField(null=True, blank=True)

    tags = models.ManyToManyField(ContextTag)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time']

    def get_treated(self):
        return self.treated
    
    def set_treated(self, value):
        self.treated = value

    a_it = property(get_treated, set_treated)

    def get_treatment_probability(self):
        return self.treatment_probability

    def set_treatment_probability(self, value):
        self.treatment_probability = value

    pi_it = property(get_treatment_probability, set_treatment_probability)

    def decide(self):
        if self.test:
            self.treated = True
            self.treatment_probability = 1
            self.save()
            return True
        if not self.available:
            self.a_it = False
            self.save()
            return self.a_it
        if not self.pi_it:
            if not hasattr(settings, 'RANDOMIZATION_FIXED_PROBABILITY'):
                raise ImproperlyConfigured("No RANDOMIZATION_FIXED_PROBABILITY")
            self.pi_it = settings.RANDOMIZATION_FIXED_PROBABILITY
        self.a_it = random.random() < self.pi_it
        self.save()
        return self.a_it

    @property
    def notification(self):
        if hasattr(self, '_notification'):
            return self._notification
        message_content_type = ContentType.objects.get_for_model(Message)
        context_objects = DecisionContext.objects.filter(
            decision = self,
            content_type = message_content_type
        ).all()
        for message in [obj.content_object for obj in context_objects]:
            if message.message_type == Message.NOTIFICATION:
                self._notification = message
                return self._notification
        return False

    def add_context_object(self, object):
        DecisionContext.objects.create(
            decision = self,
            content_object = object
        )

    def get_context(self):
        return [tag.tag for tag in self.tags.all()]

    def add_context(self, tag_text):
        tag, _ = ContextTag.objects.get_or_create(
            tag = tag_text
        )
        self.tags.add(tag)

    def remove_contexts(self, tags_text):
        for tag in ContextTag.objects.filter(tag__in=tags_text).all():
            self.tags.remove(tag)

    def is_complete(self):
        if self.a_it is not None:
            return True
        else:
            return False

    def __str__(self):
        formatted_time = self.time.strftime("%Y-%m-%d at %H:%M")
        if self.a_it is None:
            return "On %s for %s (undecided)" % (formatted_time, self.user)
        else:
            return "On %s for %s (decided)" % (formatted_time, self.user)

class DecisionContext(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.ForeignKey(Decision)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
