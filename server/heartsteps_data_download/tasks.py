import datetime
import json
import os
import subprocess

from celery import shared_task
from django.conf import settings
from import_export import resources
from import_export.fields import Field

from adherence_messages.models import AdherenceMetric
from adherence_messages.services import AdherenceService
from anti_sedentary.admin import AntiSedentaryDecisionResouce
from anti_sedentary.models import AntiSedentaryDecision
from anti_sedentary.models import AntiSedentaryServiceRequest
from days.services import DayService
from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService
from page_views.models import PageView
from participants.models import Participant
from participants.models import Cohort
from participants.tasks import export_cohort_data
from push_messages.models import Message
from service_requests.admin import ServiceRequestResource
from walking_suggestions.admin import WalkingSuggestionDecisionResource
from walking_suggestions.models import Configuration
from walking_suggestions.models import WalkingSuggestionDecision
from walking_suggestions.models import WalkingSuggestionServiceRequest
from watch_app.services import StepCountService as WatchAppStepCountService

EXPORT_DIRECTORY = '/heartsteps-export'

def write_csv_file(directory, filename, content):
    file = open(os.path.join(directory, filename), 'w')
    file.write(content)
    file.close()







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
    export_adherence_metrics(username=username, directory=user_directory)
    subprocess.call(
        'gsutil -m rsync %s gs://%s' % (user_directory, settings.HEARTSTEPS_NIGHTLY_DATA_BUCKET),
        shell=True
    )

@shared_task
def download_data():
    if not hasattr(settings, 'HEARTSTEPS_NIGHTLY_DATA_BUCKET') or not settings.HEARTSTEPS_NIGHTLY_DATA_BUCKET:
        print('Data download not configured')
        return False
    if not os.path.exists(EXPORT_DIRECTORY):
        os.makedirs(EXPORT_DIRECTORY)
    for cohort in Cohort.objects.all():
        cohort_directory = os.path.join(EXPORT_DIRECTORY, 'cohort-'+cohort.slug)
        if not os.path.exists(cohort_directory):
            os.makedirs(cohort_directory)
        export_cohort_data(
            cohort_name = cohort.name,
            directory = cohort_directory
        )
        subprocess.call(
            'gsutil -m rsync %s gs://%s' % (cohort_directory, settings.HEARTSTEPS_NIGHTLY_DATA_BUCKET),
            shell=True
        )

@shared_task
def queued_export_user_data(usernames):
    if len(usernames):
        username = usernames.pop()
        print('Exporting %s (%d remaining)' % (username,len(usernames)))
        try:
            export_user_data(username)
        except:
            print('Error exporting %s' % (username))
        print('Export complete %s' % (username))
        queued_export_user_data.apply_async(kwargs={
            'usernames': usernames
        })
    else:
        print('Done exporting')
