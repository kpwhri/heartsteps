import uuid
from random import randint
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from locations.models import Location
from locations.factories import get_last_user_location, determine_location_type
from weather.models import WeatherForecast
from weather.functions import WeatherFunction
from push_messages.models import Message as PushMessage
from push_messages.services import PushMessageService

class ContextTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=25)

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

    def get_context(self):
        try:
            push_message_service = PushMessageService(self.user)
        except PushMessageService.DeviceMissingError:
            return False
        message = push_message_service.send_data(self.user, {
            'type': 'get_context'
        })
        if message:
            return True
        else:
            return False

    def add_location_context(self):
        location = get_last_user_location(self.user)
        if location:
            location_type = determine_location_type(
                user = self.user,
                latitude = location.latitude,
                longitude = location.longitude
            )
            self.add_context(location_type)
            DecisionContext.objects.create(
                decision = self,
                content_object = location
            )

            forecast, weather_context = WeatherFunction.get_context(
                latitude = location.latitude,
                longitude = location.longitude
            )
            self.add_context(weather_context)
            DecisionContext.objects.create(
                decision = self,
                content_object = forecast
            )
        else:
            self.add_context("other")    

    def add_context(self, tag_text):
        tag, created = ContextTag.objects.get_or_create(
            tag = tag_text
        )
        self.tags.add(tag)

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
    sent_message = models.OneToOneField(PushMessage, null=True, blank=True)

    def get_message_template_tags(self):
        message_tags_query = models.Q()
        for tag in self.decision.tags.all():
            message_tags_query |= models.Q(tag=tag.tag)
        return MessageTag.objects.filter(message_tags_query).all()

    def get_message_template(self):
        query = MessageTemplate.objects
        for tag in self.get_message_template_tags():
            query = query.filter(context_tags__in=[tag])
        message_templates = query.all()

        if len(message_templates) == 0:
            return False
        if len(message_templates) == 1:
            return message_templates[0]
        return message_templates[randint(0, len(message_templates)-1)]

    def send_message(self):
        try:
            push_message_service = PushMessageService(self.decision.user)
        except PushMessageService.DeviceMissingError:
            return False
        message = push_message_service.send_notification(
            self.decision.user,
            self.message_template.title,
            self.message_template.body
            )
        if message:
            self.sent_message = message
            self.save()
            return True
        return False
