import os
import pytz
import json
import random
from celery import shared_task
from datetime import timedelta, datetime, date
import requests

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from days.services import DayService
from participants.models import Participant
from randomization.models import UnavailableReason
from service_requests.admin import ServiceRequestResource

from .models import SuggestionTime
from .models import Configuration
from .models import WalkingSuggestionDecision
from .models import WalkingSuggestionServiceRequest
from .models import NightlyUpdate
from .models import PoolingServiceConfiguration
from .models import PoolingServiceRequest
from .resources import WalkingSuggestionDecisionResource
from .services import WalkingSuggestionService
from .services import WalkingSuggestionDecisionService
from .services import WalkingSuggestionTimeService

@shared_task
def queue_walking_suggestion(username):
    service = WalkingSuggestionTimeService(username=username)
    category = service.suggestion_time_category_at(timezone.now())
    random_minutes = random.randint(15,30)
    create_walking_suggestion.apply_async(
        countdown = random_minutes * 60,
        kwargs = {
            'username': username
        }
    )

@shared_task
def create_walking_suggestion(username):
    try:
        WalkingSuggestionDecisionService.make_decision_now(username=username)
    except WalkingSuggestionDecisionService.RandomizationUnavailable:
        pass

@shared_task
def nightly_update(username, day_string):
    dt = datetime.strptime(day_string, '%Y-%m-%d')
    day = date(dt.year, dt.month, dt.day)
    try:
        service = WalkingSuggestionService(username=username)
        service.nightly_update(day)
    except WalkingSuggestionService.Unavailable:
        return None

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

@shared_task
def update_pooling_service():
    if not hasattr(settings, 'POOLING_SERVICE_URL') or not settings.POOLING_SERVICE_URL:
        return False
    url = settings.POOLING_SERVICE_URL
    
    users = [configuration.user for configuration in PoolingServiceConfiguration.objects.all()]
    
    participants = {}
    for user in users:
        participants[user.username] = {'username':user.username}

    for participant in Participant.objects.filter(user__in=users).all():
        username = participant.user.username
        participants[username]['cohort'] = participant.cohort.name
        participants[username]['study'] = participant.cohort.study.name
    for configuration in Configuration.objects.filter(user__in=users).all():
        username = configuration.user.username
        participants[username]['start'] = configuration.service_initialized_date.strftime('%Y-%m-%d')

    data = {
        'participants': [participants[x] for x in participants.keys()]
    }

    request_record = PoolingServiceRequest.objects.create(
        name = 'Pooling service update',
        url = url,
        request_data = json.dumps(data),
        request_time = timezone.now()
    )

    response = requests.post(url, json=data)

    request_record.response_code = response.status_code
    request_record.response_data = response.text
    request_record.response_time = timezone.now()
    request_record.save()
    

def export_walking_suggestion_decisions(username, directory, filename=None):
    if not filename:
        filename = '%s.walking_suggestion_decisions.csv' % (username)

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

    _file = open(os.path.join(directory, filename), 'w')
    
    start_index = 0
    slice_size = 100
    first = True
    start = timezone.now()
    loop_time = timezone.now()
    print('start export of %d decisions' % (total_rows))
    while start_index < total_rows:
        end_index = start_index + slice_size
        if end_index >= total_rows:
            end_index = total_rows - 1
        decisions = queryset[start_index:end_index]
        decision_ids = [_decision.id for _decision in decisions]
        unavailable_reasons = {}
        for _id in decision_ids:
            unavailable_reasons[_id] = []
        unavailable_reason_query = UnavailableReason.objects.filter(decision_id__in=decision_ids)
        print('Unavailable reasons count: %d' % (unavailable_reason_query.count()))
        for unavailable_reason in unavailable_reason_query.all():
            unavailable_reasons[unavailable_reason.decision_id].append(unavailable_reason.reason)
        new_decisions = []
        for decision in decisions:
            decision._unavailable_reasons = unavailable_reasons[decision.id]
            new_decisions.append(decision)
        dataset = WalkingSuggestionDecisionResource().export(
            queryset = new_decisions
        )
        csv = dataset.csv
        if first:
            first = False
        else:
            csv_list = csv.split('\r\n')
            csv = '\r\n'.join(csv_list[1:])
        _file.write(csv)

        diff = timezone.now() - loop_time
        print('Exported %d to %d in %d seconds' % (start_index, end_index, diff.seconds))
        loop_time = timezone.now()

        start_index = start_index + slice_size
    _file.close()
    diff = timezone.now() - start
    print('Total export time %d' % (diff.seconds))

def export_walking_suggestion_service_requests(username, directory):
    dataset = ServiceRequestResource().export(
        queryset = WalkingSuggestionServiceRequest.objects.filter(
            user__username = username
        )
    )
    filename = '%s.walking_suggestion_service_requests.csv' % (username)
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()