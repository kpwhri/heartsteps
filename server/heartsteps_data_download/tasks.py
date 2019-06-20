import datetime
import json
import os
import subprocess

from celery import shared_task
from django.conf import settings
from import_export import resources
from import_export.fields import Field

from anti_sedentary.admin import AntiSedentaryDecisionResouce
from anti_sedentary.models import AntiSedentaryDecision
from anti_sedentary.models import AntiSedentaryServiceRequest
from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService
from participants.models import Participant
from service_requests.admin import ServiceRequestResource
from walking_suggestions.admin import WalkingSuggestionDecisionResource
from walking_suggestions.models import Configuration
from walking_suggestions.models import WalkingSuggestionDecision
from walking_suggestions.models import WalkingSuggestionServiceRequest

EXPORT_DIRECTORY = '/heartsteps-export'

def write_csv_file(directory, filename, content):
    file = open(os.path.join(directory, filename), 'w')
    file.write(content)
    file.close()

class FitbitMinuteDataResource(resources.Resource):
    username = Field(attribute='username')
    fitbit_account = Field(attribute='fitbit_account')
    timezone = Field(attribute='timezone')
    date = Field(attribute='date')
    time = Field(attribute='time')
    steps = Field(attribute='steps')
    heart_rate = Field(attribute='heart_rate')

    class Meta:
        export_order = [
            'username',
            'fitbit_account',
            'timezone',
            'date',
            'time',
            'steps',
            'heart_rate'
        ]

def export_fitbit_data(username, directory):
    fitbit_service = FitbitService(username=username)
    fitbit_account = fitbit_service.account

    minute_level_data = []

    class MinuteLevelData:
        username = None
        fitbit_account = None
        timezone = None
        date = 'Date'
        time = 'Time'
        steps=0
        heart_rate=0

    days = FitbitDay.objects.filter(account=fitbit_account).all()
    for day in days:
        for minute in day.get_minute_level_data():
            _m = MinuteLevelData()
            _m.username = username
            _m.fitbit_account = fitbit_account.fitbit_user
            _m.timezone = day._timezone
            _m.date = minute['date']
            _m.time = minute['time']
            if 'steps' in minute:
                _m.steps = minute['steps']
            if 'heart_rate' in minute:
                _m.heart_rate = minute['heart_rate']
            minute_level_data.append(_m)
    
    dataset = FitbitMinuteDataResource().export(minute_level_data)
    write_csv_file(
        directory = directory,
        filename = '%s.fitbit_minutes.csv' % (username),
        content = dataset.csv
    )

def export_walking_suggestion_decisions(username, directory):
    print('- walking suggestion decisions for %s' % (username))

    try:
        configuration = Configuration.objects.get(user__username = username)
    except Configuration.DoesNotExist:
        return False
    if not configuration.service_initialized:
        return False

    day_service = DayService(user=configuration.user)
    initialized_datetime = day_service.get_datetime_at(configuration.service_initialized_date)

    queryset = WalkingSuggestionDecision.objects.filter(
        user = configuration.user,
        time__gt = initialized_datetime
    )
    total_rows = queryset.count()

    print('Total rows: %s' % (total_rows))

    filename = '%s.walking_suggestion_decisions.csv' % (username)
    _file = open(os.path.join(directory, filename), 'w')
    
    start_index = 0
    slice_size = 100
    first = True
    while start_index < total_rows:
        end_index = start_index + slice_size
        if end_index >= total_rows:
            end_index = total_rows - 1
        print('Get rows %d to %d' % (start_index, end_index))
        dataset = WalkingSuggestionDecisionResource().export(
            queryset = queryset[start_index:end_index]
        )
        csv = dataset.csv
        if first:
            first = False
        else:
            csv_list = csv.split('\r\n')
            csv = '\r\n'.join(csv_list[1:])
        _file.write(csv)
        print('--> wrote data %d to %d' % (start_index, end_index))
        start_index = start_index + slice_size
    _file.close()
    print('Done')

def export_walking_suggestion_service_requests(username, directory):
    print('- walkling suggestion service_requests')
    dataset = ServiceRequestResource().export(
        queryset = WalkingSuggestionServiceRequest.objects.filter(
            user__username = username
        )
    )
    write_csv_file(
        directory = directory,
        filename = '%s.walking_suggestion_service_requests.csv' % (username),
        content = dataset.csv
    )

def export_anti_sedentary_decisions(username, directory):
    print('- anti-sedentary decisions for %s' % (username))

    queryset = AntiSedentaryDecision.objects.filter(user__username=username)
    total_rows = queryset.count()
    print('Total rows: %d' % total_rows)
    filename = '%s.anti_sedentary_decisions.csv' % (username)
    _file = open(os.path.join(directory, filename), 'w')
    start_index = 0
    slice_size = 100
    first = True
    while start_index < total_rows:
        end_index = start_index + slice_size
        if end_index >= total_rows:
            end_index = total_rows - 1
        dataset = AntiSedentaryDecisionResouce().export(
            queryset = queryset[start_index:end_index]
        )
        csv = dataset.csv
        if first:
            first = False
        else:
            csv_list = csv.split('\r\n')
            csv = '\r\n'.join(csv_list[1:])
        _file.write(dataset.csv)
        print('--> wrote data %d to %d' % (start_index, end_index))
        start_index = start_index + slice_size
    _file.close()
    print('Done')

def export_anti_sedentary_service_requests(username, directory):
    print('- anti-sedentary service requests')
    dataset = ServiceRequestResource().export(
        queryset = AntiSedentaryServiceRequest.objects.filter(
            user__username = username
        )
    )
    write_csv_file(
        directory = directory,
        filename = '%s.anti_sedentary_service_requests' % (username),
        content = dataset.csv
    )

@shared_task
def export_user_data(username):
    if not hasattr(settings, 'HEARTSTEPS_NIGHTLY_DATA_BUCKET') or not settings.HEARTSTEPS_NIGHTLY_DATA_BUCKET:
        print('Data download not configured')
        return False
    if not os.path.exists(EXPORT_DIRECTORY):
        os.makedirs(EXPORT_DIRECTORY)
    user_directory = os.path.join(EXPORT_DIRECTORY, username)
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
    print(username)
    export_walking_suggestion_decisions(username=username, directory=user_directory)
    export_walking_suggestion_service_requests(username=username, directory=user_directory)
    export_anti_sedentary_decisions(username=username, directory=user_directory)
    export_anti_sedentary_service_requests(username=username, directory=user_directory)
    export_fitbit_data(username=username, directory=user_directory)
    subprocess.call(
        'gsutil -m rsync %s gs://%s' % (user_directory, settings.HEARTSTEPS_NIGHTLY_DATA_BUCKET),
        shell=True
    )


@shared_task
def download_data():
    for participant in Participant.objects.exclude(user=None).all():
        export_user_data.apply_async(kwargs={
            'username': participant.user.username
        })
