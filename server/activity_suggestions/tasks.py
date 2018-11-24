import pytz
from celery import shared_task
from datetime import timedelta, datetime

from django.utils import timezone
from django.contrib.auth.models import User

from randomization.models import Decision
from activity_suggestions.models import SuggestionTime, Configuration, ActivitySuggestionDecision
from activity_suggestions.services import ActivitySuggestionService, ActivitySuggestionDecisionService

@shared_task
def initialize_activity_suggestion_service(username):
    try:
        configuration = Configuration.objects.get(user__username=username)
    except Configuration.DoesNotExist:
        return False
    try:
        service = ActivitySuggestionService(configuration)
    except ActivitySuggestionService.Unavailable:
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
        service = ActivitySuggestionService(configuration)
    except ActivitySuggestionService.Unavailable:
        return False
    service.update(yesterday)

@shared_task
def start_decision(username, category):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False

    decision_time = timezone.now() + timedelta(minutes=10)
    decision = ActivitySuggestionDecision.objects.create(
        user = user,
        time = decision_time
    )
    decision.add_context("activity suggestion")
    decision.add_context(category)

    decision_service = ActivitySuggestionDecisionService(decision)
    decision_service.request_context()

    make_decision.apply_async(kwargs={
        'decision_id': str(decision_service.decision.id)
    }, eta=decision_time)

@shared_task
def make_decision(decision_id):
    decision = Decision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision_service = ActivitySuggestionDecisionService(decision)
    decision_service.update_context()

    if decision_service.decide():
        decision_service.create_message()
        decision_service.send_message()
