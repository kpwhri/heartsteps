import pytz
from celery import shared_task
from datetime import timedelta, datetime

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from .models import SuggestionTime, Configuration, WalkingSuggestionDecision
from .services import WalkingSuggestionService, WalkingSuggestionDecisionService, WalkingSuggestionTimeService

@shared_task
def create_decision(username):
    try:
        service = WalkingSuggestionTimeService(username=username)
        category = service.suggestion_time_category_available_at(timezone.now())
    except WalkingSuggestionTimeService.Unavailable:
        return False
    if category:
        decision = service.create_decision(
            category = category,
            time = timezone.now()
        )
        make_decision.apply_async(kwargs={
            'decision_id': str(decision.id)
        })

@shared_task
def start_decision(username, category):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    service = WalkingSuggestionDecisionService.create_decision(
        user = user,
        category = category
    )
    make_decision.apply_async(kwargs={
        'decision_id': str(service.decision.id)
    })

@shared_task
def make_decision(decision_id):
    decision = WalkingSuggestionDecision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision_service = WalkingSuggestionDecisionService(decision)
    decision_service.update_context()

    if decision_service.decide():
        decision_service.send_message()
