from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from daily_tasks.models import DailyTask
from fitbit_api.services import FitbitDayService
from locations.services import LocationService
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration

from participants.models import Participant

@shared_task
def initialize_participant(username):
    participant = Participant.objects.get(user__username = username)

    if not hasattr(settings, 'PARTICIPANT_NIGHTLY_UPDATE_TIME'):
        raise ImproperlyConfigured('Participant nightly update time not configured')
    update_hour, update_minute = settings.PARTICIPANT_NIGHTLY_UPDATE_TIME.split(':')
    DailyTask.create_daily_task(
        user = participant.user,
        category = 'participant update',
        task = 'participants.tasks.nightly_update',
        name = '%s nightly update' % (participant.user.username),
        arguments = {
            'username': participant.user.username
        },
        hour = int(update_hour),
        minute = int(update_minute)
    )

    WalkingSuggestionConfiguration.objects.update_or_create(user=participant.user)

@shared_task
def nightly_update(username):
    try:
        participant = Participant.objects.get(user__username = username)
    except Participant.DoesNotExist:
        return False
    
    location_service = LocationService(participant.user)
    timezone = location_service.get_current_timezone()
    yesterday = datetime.now(timezone) - timedelta(days=1)

    ## Create "Onboarding app" to contain this logic
    # If participant doesn't have active push device
    # AND datetime > number of days for baseline
    # Send text message prompt

    # Study adherence nightly update run
    ## Looks at participant data, sends activity alerts

    fitbit_day = FitbitDayService(
        user = participant.user,
        date = yesterday
    )
    fitbit_day.update()

    ## Maybe following is just update task from app
    # if walking suggestions configuration has suggestion times
    # AND
    # activity suggestion service is available
    # THEN
    # if service not initialized, initialize service
    # else update service
