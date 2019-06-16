import datetime
import os
import subprocess

from celery import shared_task
from django.conf import settings

from anti_sedentary.admin import AntiSedentaryDecisionResouce
from anti_sedentary.models import AntiSedentaryDecision
from anti_sedentary.models import AntiSedentaryServiceRequest
from days.services import DayService
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

def export_walking_suggestion_decisions(username, directory):
    print('- walking suggestion decisions')
    try:
        configuration = Configuration.objects.get(user__username = username)
    except Configuration.DoesNotExist:
        return False
    if not configuration.service_initialized:
        return False

    day_service = DayService(user=configuration.user)
    initialized_datetime = day_service.get_datetime_at(configuration.service_initialized_date)
    
    dataset = WalkingSuggestionDecisionResource().export(
        queryset = WalkingSuggestionDecision.objects.filter(
            user = configuration.user,
            time__gt = initialized_datetime
        )
    )
    write_csv_file(
        directory = directory,
        filename = '%s.walking_suggestion_decisions.csv' % (username),
        content = dataset.csv
    )

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
    print('- anti-sedentary decisions')
    dataset = AntiSedentaryDecisionResouce().export(
        queryset = AntiSedentaryDecision.objects.filter(
            user__username = username
        )
    )
    write_csv_file(
        directory = directory,
        filename = '%s.anti_sedentary_decisions.csv',
        content = dataset.csv
    )

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
    # export_anti_sedentary_decisions(username=username, directory=user_directory)
    export_anti_sedentary_service_requests(username=username, directory=user_directory)
    
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
