import uuid
from django.db import models

from django.contrib.auth.models import User
from heartsteps_messages.models import Message

class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    a_it = models.NullBooleanField(null=True, blank=True)
    pi_it = models.FloatField(null=True, blank=True)
    message = models.ForeignKey(Message, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_context(self):
        print("... get context ...")

    def get_message(self):
        print("... make a message to send ...")

    def send_message(self):
        if self.message:
            return self.message.send()
        return False

    def __str__(self):
        if self.message:
            return "For %s (messaged)" % self.user
        elif self.a_it is None:
            return "For %s (undecided)" % self.user
        else:
            return "For %s (decided)" % self.user
