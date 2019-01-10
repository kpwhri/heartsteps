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
def initialize_activity_suggestion_service(username):
    try:
        configuration = Configuration.objects.get(user__username=username)
    except Configuration.DoesNotExist:
        return False
    try:
        service = WalkingSuggestionService(configuration)
    except WalkingSuggestionService.Unavailable:
        return False
    service.initialize()

@shared_task
def update_activity_suggestion_service(username):
    try:
        configuration = Configuration.objects.get(user__username=username)
    except Configuration.DoesNotExist:
        return False
    yesterday = datetime.now(configuration.timezone) - timedelta(days=1)
    try:
        service = WalkingSuggestionService(configuration)
    except WalkingSuggestionService.Unavailable:
        return False
    service.update(yesterday)

@shared_task
def start_decision(username, category):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    if not hasattr(settings, 'WALKING_SUGGESTION_TIME_OFFSET'):
        raise ImproperlyConfigured('No walking suggestion time offset')

    decision_time = timezone.now() + timedelta(minutes=settings.WALKING_SUGGESTION_TIME_OFFSET)
    decision = WalkingSuggestionDecision.objects.create(
        user = user,
        time = decision_time
    )
    decision.add_context(category)

    request_decision_context.apply_async(kwargs={
        'decision_id': str(decision.id)
    })

@shared_task
def request_decision_context(decision_id):
    decision = WalkingSuggestionDecision.objects.get(id=decision_id)

    if not hasattr(settings, 'WALKING_SUGGESTION_REQUEST_RETRY_TIME'):
        raise ImproperlyConfigured('No walking suggestion request retry time')
    if not hasattr(settings, 'WALKING_SUGGESTION_REQUEST_RETRY_ATTEMPTS'):
        raise ImproperlyConfigured('No walking suggestion request retry attempts')

    if decision.is_complete():
        return False
    decision_service = WalkingSuggestionDecisionService(decision)
    decision_service.request_context()

    if len(decision_service.get_context_requests()) > settings.WALKING_SUGGESTION_REQUEST_RETRY_ATTEMPTS:
        if decision_service.can_impute_context():
            make_decision.apply_async(kwargs={
                'decision_id': decision_id
            })
    else:
        request_decision_context.apply_async(kwargs={
            'decision_id': decision_id
        }, eta=timezone.now() + timedelta(minutes=settings.WALKING_SUGGESTION_REQUEST_RETRY_TIME))

@shared_task
def make_decision(decision_id):
    decision = WalkingSuggestionDecision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision_service = WalkingSuggestionDecisionService(decision)
    decision_service.update_context()

    if decision_service.decide():
        decision_service.send_message()
