# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.contrib.auth.models import User
from .models import Decision


@shared_task
def make_decision(decision_id):
    decision = Decision.objects.get(id=decision_id)
    
    if not hasattr(decision, 'location'):
        decision.get_context()
        return

    if decision.decide():
        decision.make_message()
        decision.send_message()