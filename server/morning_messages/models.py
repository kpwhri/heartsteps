from django.db import models

from behavioral_messages.models import MessageTemplate, ContextTag

class AnchorMessage(models.Model):
    body = models.CharField(max_length=255)
    context_tags = models.ManyToManyField(ContextTag)

    def __str__(self):
        return self.body

class MorningMessage(models.Model):
    message_template = models.ForeignKey(MessageTemplate)
    anchor_message = models.ForeignKey(AnchorMessage)

    context_tags = models.ManyToManyField(ContextTag)

    def __str__(self):
        return self.message_template.body