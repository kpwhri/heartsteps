import uuid
import requests
from django.db import models

from django.contrib.auth.models import User

class ContextTag(models.Model):
    """
    Used to organize and filter message templates
    """
    tag = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.tag

class MessageTemplate(models.Model):
    """
    Message templates used to populate messages that are sent to users
    """
    title = models.CharField(max_length=100, null=True, blank=True)
    body = models.CharField(max_length=255)

    context_tags = models.ManyToManyField(ContextTag)

    def __str__(self):
        return self.body

    def add_context(self, tag_text):
        tag, _ = ContextTag.objects.get_or_create(tag = tag_text)
        self.context_tags.add(tag)

    def remove_context(self, tag_text):
        tag, _ = ContextTag.objects.get_or_create(tag = tag_text)
        self.context_tags.remove(tag)