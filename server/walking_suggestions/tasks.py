import pytz
from celery import shared_task
from datetime import timedelta, datetime

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from .models import SuggestionTime, Configuration, WalkingSuggestionDecision
from .services import WalkingSuggestionService, WalkingSuggestionDecisionService

@shared_task
def start_decision(username, category):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    if not hasattr(settings, 'WALKING_SUGGESTION_TIME_OFFSET'):
        raise ImproperlyConfigured('No walking suggestion time offset')

    decision_time = timezone.now() + timedelta(minutes=settings.WALKING_SUGGESTION_TIME_OFFSET)
    service = WalkingSuggestionDecisionService.create_decision(
        user = user,
        category = category,
        time = decision_time
    )
    request_decision_context.apply_async(kwargs={
        'decision_id': str(service.decision.id)
    })

@shared_task
def request_decision_context(decision_id):
    if not hasattr(settings, 'WALKING_SUGGESTION_REQUEST_RETRY_TIME'):
        raise ImproperlyConfigured('No walking suggestion request retry time')
    if not hasattr(settings, 'WALKING_SUGGESTION_REQUEST_RETRY_ATTEMPTS'):
        raise ImproperlyConfigured('No walking suggestion request retry attempts')
    
    decision = WalkingSuggestionDecision.objects.get(id=decision_id)
    decision_service = WalkingSuggestionDecisionService(decision)

    if not decision.is_complete():
        if len(decision_service.get_context_requests()) > settings.WALKING_SUGGESTION_REQUEST_RETRY_ATTEMPTS:
            decision.available = False
            decision.unavailable_reason = 'Unreachable'
            decision.save()
            make_decision.apply_async(kwargs={
                'decision_id': decision_id
            })
        else:
            try:
                decision_service.request_context()
                request_decision_context.apply_async(kwargs={
                    'decision_id': decision_id
                }, eta=timezone.now() + timedelta(minutes=settings.WALKING_SUGGESTION_REQUEST_RETRY_TIME))
            except WalkingSuggestionDecisionService.Unreachable as error:
                decision.available = False
                decision.unavailable_reason = error
                decision.save()
                make_decision.apply_async(kwargs={
                    'decision_id': decision_id
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
