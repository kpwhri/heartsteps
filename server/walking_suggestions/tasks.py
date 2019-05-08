import pytz
from celery import shared_task
from datetime import timedelta, datetime, date

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from .models import SuggestionTime, Configuration, WalkingSuggestionDecision, NightlyUpdate
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
    pass

@shared_task
def make_decision(decision_id):
    decision = WalkingSuggestionDecision.objects.get(id=decision_id)
    if decision.is_complete():
        return False
    
    decision_service = WalkingSuggestionDecisionService(decision)
    decision_service.update()
    if decision_service.decide():
        decision_service.send_message()

@shared_task
def nightly_update(username, day_string):
    dt = datetime.strptime(day_string, '%Y-%m-%d')
    day = date(dt.year, dt.month, dt.day)
    try:
        service = WalkingSuggestionService(username=username)
    except WalkingSuggestionService.Unavailable:
        return None
    if not service.is_initialized():
        service.initialize(date=day)
    else:
        configuration = Configuration.objects.get(user__username = username)
        last_update_query = NightlyUpdate.objects.filter(
            user = configuration.user,
            updated = True,
            day__gt = configuration.service_initialized_date
        )
        if last_update_query.count() > 0:
            last_updated_day = last_update_query.last().day
        else:
            last_updated_day = configuration.service_initialized_date
        last_updated_day = last_updated_day + timedelta(days=1)
        while last_updated_day <= day:
            service.update(date=last_updated_day)
            NightlyUpdate.objects.update_or_create(
                user = configuration.user,
                day = last_updated_day,
                defaults = {
                    'updated': True
                }
            )
            last_updated_day = last_updated_day + timedelta(days=1)

