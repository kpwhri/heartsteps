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

    filename = '%s.walking_suggestion_decisions.csv' % (username)
    _file = open(os.path.join(directory, filename), 'w')
    
    start_index = 0
    slice_size = 100
    first = True
    while start_index < total_rows:
        end_index = start_index + slice_size
        if end_index >= total_rows:
            end_index = total_rows - 1
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
        start_index = start_index + slice_size
    _file.close()

def export_walking_suggestion_service_requests(username, directory):
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
    queryset = AntiSedentaryDecision.objects.filter(user__username=username)
    total_rows = queryset.count()
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
        start_index = start_index + slice_size
    _file.close()

def export_anti_sedentary_service_requests(username, directory):
    dataset = ServiceRequestResource().export(
        queryset = AntiSedentaryServiceRequest.objects.filter(
            user__username = username
        )
    )
    write_csv_file(
        directory = directory,
        filename = '%s.anti_sedentary_service_requests.csv' % (username),
        content = dataset.csv
    )

class DailyAdherenceResource(resources.Resource):
    date = Field()

    app_installed = Field()
    app_page_views = Field()
    app_used = Field()

    fitbit_worn = Field()
    fitbit_updated = Field()
    
    minutes_worn = Field()
    fitbit_step_count = Field()
    watch_app_step_count = Field()

    messages_sent = Field()
    messages_received = Field()
    messages_opened = Field()
    messages_engaged = Field()

    anti_sedentary_messages_sent = Field()
    anti_sedentary_messages_received = Field()
    anti_sedentary_messages_opened = Field()
    anti_sedentary_messages_engaged = Field()

    walking_suggestion_messages_sent = Field()
    walking_suggestion_messages_received = Field()
    walking_suggestion_messages_opened = Field()
    walking_suggestion_messages_engaged = Field()

    class Meta:
        export_order = [
            'date',
            'app_installed',
            'app_page_views',
            'app_used',
            'fitbit_updated',
            'minutes_worn',
            'fitbit_worn',
            'fitbit_step_count',
            'watch_app_step_count',
            'messages_sent',
            'messages_received',
            'messages_opened',
            'messages_engaged',
            'anti_sedentary_messages_sent',
            'anti_sedentary_messages_received',
            'anti_sedentary_messages_opened',
            'anti_sedentary_messages_engaged',
            'walking_suggestion_messages_sent',
            'walking_suggestion_messages_received',
            'walking_suggestion_messages_opened',
            'walking_suggestion_messages_engaged'
        ]
    
    def get_key(self, instance, key):
        if key in instance:
            return instance[key]
        else:
            return None

    def dehydrate_app_installed(self, instance):
        return self.get_key(instance, AdherenceMetric.APP_INSTALLED)

    def dehydrate_app_page_views(self, instance):
        return self.get_key(instance, 'app_page_views')

    def dehydrate_app_used(self, instance):
        return self.get_key(instance, AdherenceMetric.APP_USED)

    def dehydrate_fitbit_worn(self, instance):
        return self.get_key(instance, AdherenceMetric.FITBIT_WORN)

    def dehydrate_fitbit_updated(self, instance):
        return self.get_key(instance, AdherenceMetric.FITBIT_UPDATED)

    def dehydrate_date(self, instance):
        return instance['date'].strftime('%Y-%m-%d')

    def dehydrate_minutes_worn(self, instance):
        return self.get_key(instance, 'fitbit_minutes_worn')

    def dehydrate_fitbit_step_count(self, instance):
        return self.get_key(instance, 'fitbit_step_count')

    def dehydrate_watch_app_step_count(self, instance):
        return self.get_key(instance, 'watch_app_step_count')

    def dehydrate_messages_sent(self, instance):
        return self.get_key(instance, 'messages_sent')

    def dehydrate_messages_received(self, instance):
        return self.get_key(instance, 'messages_received')

    def dehydrate_messages_opened(self, instance):
        return self.get_key(instance, 'messages_opened')

    def dehydrate_messages_engaged(self, instance):
        return self.get_key(instance, 'messages_engaged')

    def dehydrate_anti_sedentary_messages_sent(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_sent')

    def dehydrate_anti_sedentary_messages_received(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_received')

    def dehydrate_anti_sedentary_messages_opened(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_opened')

    def dehydrate_anti_sedentary_messages_engaged(self, instance):
        return self.get_key(instance, 'anti_sedentary_messages_engaged')

    def dehydrate_walking_suggestion_messages_sent(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_sent')

    def dehydrate_walking_suggestion_messages_received(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_received')

    def dehydrate_walking_suggestion_messages_opened(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_opened')

    def dehydrate_walking_suggestion_messages_engaged(self, instance):
        return self.get_key(instance, 'walking_suggestion_messages_engaged')

def export_adherence_metrics(username, directory):
    try:
        adherence_service = AdherenceService(username = username)
    except AdherenceService.NoConfiguration:
        return False
    adherence_days = {}
    for metric in AdherenceMetric.objects.order_by('date').filter(user__username=username).all():
        date_string = metric.date.strftime('%Y-%m-%d')
        if date_string not in adherence_days:
            adherence_days[date_string] = {
                'date': metric.date
            }
        adherence_days[date_string][metric.category] = metric.value

    days = []
    for value in adherence_days.values():
        days.append(value)
    days.sort(key=lambda day: day['date'])

    try:
        fitbit_service = FitbitService(username=username)
        account = fitbit_service.account
        for day in days:
            try:
                fitbit_day = FitbitDay.objects.get(
                    account = account,
                    date = day['date']
                )
                day['fitbit_step_count'] = fitbit_day.step_count
                day['fitbit_minutes_worn'] = fitbit_day.get_minutes_worn()
            except FitbitDay.DoesNotExist:
                pass
    except FitbitService.NoAccount:
        account = None

    for day in days:
        print(day['date'])

        day_service = DayService(username = username)
        day_start = day_service.get_start_of_day(day['date'])
        day_end = day_service.get_end_of_day(day['date'])

        day['app_page_views'] = PageView.objects.filter(
            user__username = username,
            time__range = [day_start, day_end]
        ).count()

        try:
            watch_app_step_count_service = WatchAppStepCountService(username=username)
            day['watch_app_step_count'] = watch_app_step_count_service.get_step_count_between(
                start = day_start,
                end = day_end
            )
        except WatchAppStepCountService.NoStepCountRecorded:
            day['watch_app_step_count'] = None

        def tally_messages(messages, prefix='messages'):
            messages_sent = 0
            messages_received = 0
            messages_opened = 0
            messages_engaged = 0

            for message in messages:
                print(message.created, message.body)
                if message.sent:
                    messages_sent += 1
                if message.received:
                    messages_received += 1
                if message.opened:
                    messages_opened += 1
                if message.engaged:
                    messages_engaged += 1

            day[prefix + '_sent'] = messages_sent
            day[prefix + '_received'] = messages_received
            day[prefix + '_opened'] = messages_opened
            day[prefix + '_engaged'] = messages_engaged

        messages = Message.objects.filter(
            recipient__username=username,
            created__range=[day_start, day_end]
        ).all()
        tally_messages(messages)

        anti_sedentary_messages = []
        anti_sedentary_decisions = AntiSedentaryDecision.objects.filter(
            user__username = username,
            time__range = [day_start, day_end]
        ).all()
        for decision in anti_sedentary_decisions:
            if decision.notification:
                print('anti-sedentary message at', decision.time)
                anti_sedentary_messages.append(decision.notification)
        tally_messages(anti_sedentary_messages, prefix='anti_sedentary_messages')
        
        walking_suggestion_messages = []
        walking_suggestion_decisions = WalkingSuggestionDecision.objects.filter(
            user__username = username,
            time__range = [day_start, day_end]
        ).all()
        for decision in walking_suggestion_decisions:
            if decision.notification:
                print('walking-suggestion message at', decision.time)
                walking_suggestion_messages.append(decision.notification)
        tally_messages(walking_suggestion_messages, prefix='walking_suggestion_messages')

    
    dataset = DailyAdherenceResource().export(queryset=days)
    write_csv_file(
        directory = directory,
        filename = '%s.adherence_metrics.csv' % (username),
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
    export_adherence_metrics(username=username, directory=user_directory)
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
