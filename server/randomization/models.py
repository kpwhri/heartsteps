import uuid
from random import randint
from django.db import models

from django.contrib.auth.models import User
from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from locations.models import Location
from weather.models import WeatherForecast
from push_messages.models import Message as PushMessage
from push_messages.functions import send_notification, send_data

class ContextTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=25)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    message_template = models.ForeignKey(MessageTemplate)
    sent_message = models.OneToOneField(PushMessage, null=True, blank=True)


class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    time = models.DateTimeField()

    a_it = models.NullBooleanField(null=True, blank=True)
    pi_it = models.FloatField(null=True, blank=True)

    message = models.OneToOneField(Message, null=True, blank=True)
    tags = models.ManyToManyField(ContextTag)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_complete(self):
        if self.a_it is not None:
            return True
        else:
            return False

    def get_context(self):
        message = send_data(self.user, {
            'type': 'get_context',
            'decision_id': str(self.id)
        })
        if message:
            return True
        else:
            return False

    def add_context(self, tag_text):
        tag, created = ContextTag.objects.get_or_create(
            tag = tag_text
        )
        self.tags.add(tag)
        self.save()

    def decide(self):
        self.a_it = True
        self.pi_it = float(1)
        self.save()

        return True

    def get_message_template(self):
        message_tags_query = models.Q()
        for tag in self.tags.all():
            message_tags_query |= models.Q(tag=tag.tag)
        message_tags = MessageTag.objects.filter(message_tags_query).all()


        query = MessageTemplate.objects
        for tag in message_tags:
            query = query.filter(context_tags__in=[tag])
        message_templates = query.all()

        if len(message_templates) < 1:
            return False
        if len(message_templates) == 1:
            return message_templates[0]
        return message_templates[randint(0, len(message_templates)-1)]

    def make_message(self):
        message_template = self.get_message_template()
        if not message_template:
            return False
        
        message = Message.objects.create(
            message_template=message_template
        )
        self.message = message
        self.save()

    def send_message(self):
        if hasattr(self, 'message'):
            message = send_notification(
                self.user,
                self.message.message_template.title,
                self.message.message_template.body
                )
            if message:
                self.message.sent_message = message
                self.message.save()
                return True
        return False

    def __str__(self):
        if self.message and self.message.sent:
            return "For %s (messaged)" % self.user
        elif self.a_it is None:
            return "For %s (undecided)" % self.user
        else:
            return "For %s (decided)" % self.user