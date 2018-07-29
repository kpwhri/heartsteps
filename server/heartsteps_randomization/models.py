import uuid
from django.db import models

from django.contrib.auth.models import User
from heartsteps_messages.models import Message, ContextTag
from fcm_django.models import FCMDevice

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
            device = FCMDevice.objects.get(user=self.user, active=True)
        except FCMDevice.DoesNotExist:
            return False
        results = device.send_message(
            data = {
                'type': 'get_context',
                'decision_id': str(self.id)
                }
            )
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
        

    def make_message(self):
        message = Message(
            reciepent=self.user
        )
        message.title = "Example Message"
        message.body = "Example Message Body"
        message.save()

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
