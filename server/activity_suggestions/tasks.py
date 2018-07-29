# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.contrib.auth.models import User
from activity_suggestions.models import SuggestionTime
from heartsteps_randomization.models import Decision

from heartsteps_randomization.tasks import make_decision


@shared_task
def start_decision(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    decision = Decision.objects.create(
        user = user
    )
    make_decision.delay(str(decision.id))

        