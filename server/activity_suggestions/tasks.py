# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import User
from activity_suggestions.models import SuggestionTime
from randomization.models import Decision

from randomization.tasks import make_decision


@shared_task
def start_decision(username, time_category):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    decision_time = timezone.now() + timedelta(minutes=10)

    decision = Decision.objects.create(
        user = user,
        time = decision_time
    )
    decision.add_context("activity suggestion")
    decision.add_context(time_category)

    decision.get_context()

    make_decision.delay.s(str(decision.id)).apply_async(eta=decision_time)
