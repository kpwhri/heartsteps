import os
import shutil
import subprocess
import csv
from datetime import date
from datetime import timedelta
from math import floor

from celery import shared_task
from django.utils import timezone
from django.conf import settings

from adherence_messages.tasks import export_daily_metrics
from anti_sedentary.tasks import export_anti_sedentary_decisions
from anti_sedentary.tasks import export_anti_sedentary_service_requests
from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.tasks import export_fitbit_data
from fitbit_activities.tasks import export_missing_fitbit_data
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Location
from locations.models import Place
from locations.services import LocationService
from locations.tasks import export_location_count_csv
from locations.tasks import update_location_categories
from morning_messages.tasks import export_morning_message_survey
from morning_messages.tasks import export_morning_messages
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.tasks import export_walking_suggestion_decisions
from walking_suggestions.tasks import export_walking_suggestion_service_requests
from watch_app.tasks import export_step_count_records_csv
from weekly_reflection.models import ReflectionTime

from .services import ParticipantService
from .models import Cohort
from .models import DataExport
from .models import DataExportSummary
from .models import DataExportQueue
from .models import Study
from .models import Participant

@shared_task
def reset_test_participants(date_joined=None, number_of_days=9):
    current_year = date.today().strftime('%Y')

    study, _ = Study.objects.get_or_create(name='Test')
    cohort, _ = Cohort.objects.get_or_create(
        name = "test",
        study = study
    )

    try:
        participant = Participant.objects.get(heartsteps_id = 'test-new')
        participant.delete()
    except Participant.DoesNotExist:
        pass
    Participant.objects.create(
        heartsteps_id = 'test-new',
        enrollment_token = 'test-new1',
        birth_year = current_year,
        cohort = cohort
    )

    try:
        participant = Participant.objects.get(heartsteps_id = 'test')
        participant.delete()
    except Participant.DoesNotExist:
        pass
    participant = Participant.objects.create(
        heartsteps_id = 'test',
        enrollment_token = 'test-test',
        birth_year = current_year,
        cohort = cohort
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
        address = '1730 Minor Avenue, Seattle, Washington, United States of America',
        latitude = 47.6129,
        longitude = -122.327
    )
    ws_configuration, _ = WalkingSuggestionConfiguration.objects.update_or_create(
        user=user,
        defaults = {
            'enabled': True
        }
    )
    ws_configuration.set_default_walking_suggestion_times()
    ReflectionTime.objects.update_or_create(
        user = user,
        defaults = {
            'day': 'sunday',
            'time': '19:00'
        }
    )

    # Clear and re-create activity data
    Day.objects.filter(user=user).all().delete()
    FitbitDay.objects.filter(account=fitbit_account).all().delete()

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


def export_user_locations(username, directory=None, filename=None, start=None, end=None):
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.locations.csv' % (username)

    locations_query = Location.objects.filter(user__username=username)
    if start:
        locations_query = locations_query.filter(
            time__gte=start
        )
    if end:
        locations_query = locations_query.filter(
            time__lte=end
        )

    locations = []
    for _location in locations_query.order_by('time').all():
        locations.append([
            _location.id,
            username,
            _location.local_time.strftime('%Y-%m-%d %H:%M:%S'),
            _location.timezone.zone,
            _location.source,
            _location.category
        ])
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(
        [[
            'ID',
            'HeartSteps ID',
            'Time',
            'Timezone',
            'Location Source',
            'Location Category'
        ]] + locations
    )

def setup_exports(participant, directory, log_export=True):
    def export_file(fn, filename):
        filename = '{study}.{cohort}.{heartsteps_id}.{filename}'.format(
            filename = filename,
            heartsteps_id = participant.heartsteps_id,
            cohort = participant.cohort.slug,
            study = participant.cohort.study.slug
        )

        if log_export:
            print('Export start: {}'.format(filename))
            export = DataExport(
                user = participant.user,
                filename = filename,
                start = timezone.now()
            )
            try:
                fn(
                    username = participant.user.username,
                    filename = filename,
                    directory = directory,
                    start = participant.study_start,
                    end = participant.study_end
                )
            except Exception as e:
                print('Error:', e)
                export.error_message = e
            export.end = timezone.now()
            export.save()

            summary, _ = DataExportSummary.objects.get_or_create(
                user = participant.user,
                category = export.category
            )
            summary.last_data_export = export
            summary.save()

            diff = export.end - export.start
            minutes = floor(diff.seconds/60)
            seconds = diff.seconds - (minutes*60)
            print('Export end: {} ({} minutes {} seconds)'.format(filename, minutes, seconds))
        else:
            start = timezone.now()
            print('Export start: {}'.format(filename))
            fn(
                username = participant.user.username,
                filename = filename,
                directory = directory,
                start = participant.study_start,
                end = participant.study_end
            )
            end = timezone.now()
            diff = end - start
            minutes = floor(diff.seconds/60)
            seconds = diff.seconds - (minutes*60)
            print('Export end: {} ({} minutes {} seconds)'.format(filename, minutes, seconds))
    return export_file

@shared_task
def export_user_data(username, log_export=True):
    EXPORT_DIRECTORY = '/heartsteps-export'
    if not hasattr(settings, 'HEARTSTEPS_NIGHTLY_DATA_BUCKET') or not settings.HEARTSTEPS_NIGHTLY_DATA_BUCKET:
        print('Data download not configured')
        return False
    
    if log_export:
        if not os.path.exists(EXPORT_DIRECTORY):
            os.makedirs(EXPORT_DIRECTORY)
        directory = os.path.join(EXPORT_DIRECTORY, username)
        if os.path.exists(directory) and os.path.isdir(directory):
            shutil.rmtree(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
    else:
        directory = './'
    
    participant = Participant.objects.get(user__username=username)  
    export_file = setup_exports(participant, directory, log_export)

    export_file(export_anti_sedentary_decisions,
        filename = 'anti-sedentary-decisions.csv'
    )
    export_file(export_anti_sedentary_service_requests,
        filename = 'anti-sedentary-service-requests.csv'
    )
    export_file(export_daily_metrics,
        filename = 'daily-metrics.csv'
    )
    export_file(export_fitbit_data,
        filename = 'fitbit-data-per-minute.csv'
    )
    export_file(export_user_locations,
        filename = 'locations.csv'
    )
    export_file(
        export_morning_messages,
        filename = 'morning-messages.csv'
    )
    export_file(
        export_morning_message_survey,
        filename = 'morning-survey.csv'
    )
    export_file(export_walking_suggestion_decisions,
        filename = 'walking-suggestion-decisions.csv'
    )
    export_file(export_walking_suggestion_service_requests,
        filename = 'walking-suggestion-service-requests.csv'
    )

    if log_export:
        subprocess.call(
            'gsutil -m rsync %s gs://%s' % (user_directory, settings.HEARTSTEPS_NIGHTLY_DATA_BUCKET),
            shell=True
        )

def export_cohort_data(cohort_name, directory):
    cohort = Cohort.objects.get(name=cohort_name)
    participants = Participant.objects.filter(cohort=cohort).exclude(user=None).all()
    users = [p.user for p in participants]
    for _user in users:
        DataExportQueue.objects.create(
            user = user
        )

@shared_task
def daily_update(username):
    service = ParticipantService(username=username)
    day_service = DayService(username=username)
    yesterday = day_service.get_current_date() - timedelta(days=1)
    service.update(yesterday)
    if not service.participant.study_start_date:
        service.participant.study_start_date = service.participant.get_study_start_date()
        service.participant.save()
    update_location_categories(username)

@shared_task
def process_data_export_queue():
    queued_data_exports = DataExportQueue.objects.filter(
        started = None
    ).all()
    for queued_export in queued_data_exports:
        export_user_data.apply_async(kwargs={
            'username': queued_export.user.username
        })
        queued_export.started = timezone.now()
        queued_export.save()
