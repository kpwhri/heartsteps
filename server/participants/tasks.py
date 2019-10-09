from datetime import date
from datetime import timedelta

from celery import shared_task

from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Place
from locations.services import LocationService
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from weekly_reflection.models import ReflectionTime

from .services import ParticipantService
from .models import Participant

@shared_task
def daily_update(username):
    service = ParticipantService(username=username)
    day_service = DayService(username=username)
    yesterday = day_service.get_current_date() - timedelta(days=1)
    service.update(yesterday)

@shared_task
def reset_test_participants(date_joined=None, number_of_days=9):

    try:
        participant = Participant.objects.get(heartsteps_id = 'test-new')
        participant.delete()
    except Participant.DoesNotExist:
        pass
    Participant.objects.create(
        heartsteps_id = 'test-new',
        enrollment_token = 'test-new1',
        birth_year = 1980
    )

    try:
        participant = Participant.objects.get(heartsteps_id = 'test')
        participant.delete()
    except Participant.DoesNotExist:
        pass
    participant = Participant.objects.create(
        heartsteps_id = 'test',
        enrollment_token = 'test-test',
        birth_year = 1980
    )

    participant_service = ParticipantService(participant=participant)
    participant_service.initialize()

    participant = Participant.objects.get(heartsteps_id='test')
    user = participant.user

    user.is_staff = True
    user.save()

    ContactInformation.objects.update_or_create(
        user = user,
        defaults = {
            'name': 'Testy test',
            'email': 'test@nickreid.com',
            'phone': '5555555555'
        }
    )

    fitbit_account, _ = FitbitAccount.objects.get_or_create(
        fitbit_user = 'test'
    )
    FitbitAccountUser.objects.update_or_create(
        user = user,
        defaults = {
            'account': fitbit_account
        }
    )

    Place.objects.create(
        user = user,
        type = Place.HOME,
        address = 'Space Needle, Seattle, Washington, United States of America',
        latitude = 47.6205,
        longitude = -122.34899999999999
    )
    Place.objects.create(
        user = user,
        type = Place.WORK,
        address = 'Minor Avenue, Seattle, Washington, United States of America',
        latitude = 47.6129,
        longitude = -122.327
    )

    ws_configuration = WalkingSuggestionConfiguration.objects.get(
        user=user
    )
    ws_configuration.set_default_walking_suggestion_times()

    ReflectionTime.objects.create(
        user = user,
        day = 'sunday',
        time = '19:00'
    )

    
    location_service = LocationService(user = user)
    tz = location_service.get_home_timezone()
    current_dt = location_service.get_home_current_datetime()

    if date_joined:
        user.date_joined = date_joined
    else:
        user.date_joined = current_dt - timedelta(days=number_of_days)
    user.save()

    date_joined = date(
        user.date_joined.year,
        user.date_joined.month,
        user.date_joined.day
    )
    Day.objects.filter(user=user).all().delete()
    FitbitDay.objects.filter(account=fitbit_account).all().delete()
    dates_to_create = [date_joined + timedelta(days=offset) for offset in range(number_of_days)]
    dates_to_create.append(date(current_dt.year, current_dt.month, current_dt.day))
    for _date in dates_to_create:
        day, _ = FitbitDay.objects.update_or_create(
            account = fitbit_account,
            date = _date,
            defaults = {
                '_timezone': tz.zone,
                'step_count': 2000,
                '_distance': 2,
                'wore_fitbit': True
            }
        )
        # Add heartrate for every minute of the day
        dt = day.get_start_datetime()
        day_end = dt.replace(hour=20)
        while dt < day_end:
            FitbitMinuteHeartRate.objects.create(
                account = fitbit_account,
                time = dt,
                heart_rate = 1234
            )
            dt = dt + timedelta(minutes=1)
        day.save()

        Day.objects.update_or_create(
            user = user,
            date = _date,
            defaults = {
                'timezone': tz.zone
            }
        )



