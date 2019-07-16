import pytz
from celery import shared_task
from datetime import timedelta, datetime, date

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from days.services import DayService

from .models import SuggestionTime
from .models import Configuration
from .models import WalkingSuggestionDecision
from .models import NightlyUpdate
from .services import WalkingSuggestionService
from .services import WalkingSuggestionDecisionService
from .services import WalkingSuggestionTimeService

@shared_task
def nightly_update(username, day_string):
    dt = datetime.strptime(day_string, '%Y-%m-%d')
    day = date(dt.year, dt.month, dt.day)
    try:
        service = WalkingSuggestionService(username=username)
    except WalkingSuggestionService.Unavailable:
        return None
    configuration = Configuration.objects.get(user__username = username)
    if not service.is_initialized():
        NightlyUpdate.objects.filter(user = configuration.user).delete()
        service.initialize(date=day)
    else:
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

@shared_task
def initialize_and_update(username):
    configuration = Configuration.objects.get(user__username = username)
    day_service = DayService(user=configuration.user)
    walking_suggestion_service = WalkingSuggestionService(configuration=configuration)
    
    date_joined = day_service.get_date_at(configuration.user.date_joined)
    today = day_service.get_current_date()
    days_to_go_back = (today - date_joined).days
    date_range = [today - timedelta(days=offset+1) for offset in range(days_to_go_back)]

    while len(date_range):
        initialize_date = date_range.pop()
        try:
            walking_suggestion_service.get_initialization_days(initialize_date)
            break
        except WalkingSuggestionService.UnableToInitialize:
            pass
    
    walking_suggestion_service.initialize(initialize_date)
    NightlyUpdate.objects.filter(user = configuration.user).delete()
    
    while len(date_range):
        update_date = date_range.pop()
        walking_suggestion_service.update(update_date)
        NightlyUpdate.objects.create(
            user = configuration.user,
            day = update_date,
            updated = True
        )
