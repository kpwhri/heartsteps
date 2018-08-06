import uuid
from random import randint
from django.db import models

from django.contrib.auth.models import User
from heartsteps_messages.models import Message, ContextTag, Device, MessageTemplate

class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    a_it = models.NullBooleanField(null=True, blank=True)
    pi_it = models.FloatField(null=True, blank=True)

    message = models.OneToOneField(Message, null=True, blank=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(ContextTag)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_context(self):
        try:
            device = Device.objects.get(user=self.user, active=True)
        except Device.DoesNotExist:
            return False
        device.send_data({
            'type': 'get_context',
            'decision_id': str(self.id)
        })
        return True

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
        query = MessageTemplate.objects
        for tag in self.tags.all():
            query = query.filter(context_tags__in=[tag])

        message_templates = query.all()

        if len(message_templates) == 1:
            return message_templates[0]
        else :
            return message_templates[randint(0, len(message_templates)-1)]

    def make_message(self):
        message_template = self.get_message_template()

        message = Message.objects.create(
            reciepent=self.user,
            body = message_template.body
        )

        self.message = message
        self.save()

    def send_message(self):
        if self.message:
            return self.message.send()
        return False

    def __str__(self):
        if self.message and self.message.sent:
            return "For %s (messaged)" % self.user
        elif self.a_it is None:
            return "For %s (undecided)" % self.user
        else:
            return "For %s (decided)" % self.user

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.OneToOneField(
        Decision,
        on_delete=models.CASCADE
    )
    lat = models.FloatField()
    long = models.FloatField()

    def __str__(self):
        return "Location for %s" % (self.decision)
