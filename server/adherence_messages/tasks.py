from celery import shared_task
from datetime import timedelta
from datetime import date
from import_export import resources
from import_export.fields import Field
import os
import pytz

from anti_sedentary.models import AntiSedentaryDecision
from days.models import Day
from days.services import DayService
from locations.models import Location
from walking_suggestions.models import WalkingSuggestionDecision
from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService
from push_messages.models import Message
from page_views.models import PageView
from watch_app.services import StepCountService as WatchAppStepCountService

from .models import AdherenceMetric
from .services import AdherenceService

@shared_task
def initialize_adherence(username):
    service = AdherenceService(username=username)
    service.initialize()

@shared_task
def send_adherence_message(username):
    service = AdherenceService(username=username)
    service.send_adherence_message()

@shared_task
def update_adherence(username):
    service = AdherenceService(username=username)
    service.update_adherence()

class DailyAdherence:

    def __init__(self, _date):
        self.date = _date

class DailyAdherenceResource(resources.Resource):
    date = Field(column_name='Date')

    app_used = Field(
        attribute = 'app-used',
        column_name = 'App Used'
    )
    app_page_views = Field(
        attribute = 'app_page_views',
        column_name = 'App Page Views'
    )
    fitbit_step_count = Field(
        attribute = 'fitbit_step_count',
        column_name = 'Fitbit Step Count'
    )
    fitbit_minutes_worn = Field(
        attribute = 'fitbit_minutes_worn',
        column_name = 'Fitbit Minutes Worn'
    )
    fitbit_worn = Field(
        attribute = 'fitbit-worn',
        column_name = 'Fitbit Worn'
    )
    fitbit_updated = Field(
        attribute = 'fitbit-updated',
        column_name = 'Fitbit Updated'
    )
    fitbit_updated_completely = Field(
        attribute = 'fitbit-updated-completely',
        column_name = 'Fitbit Updated Completely'
    )
    location_count = Field(
        attribute = 'location_count',
        column_name = 'Number of Location Records'
    )
    messages_sent = Field(
        attribute = 'messages-sent',
        column_name = 'Messages Sent'
    )
    messages_received = Field(
        attribute = 'messages-received',
        column_name = 'Messages Received'
    )
    messages_opened = Field(
        attribute = 'messages-opened',
        column_name = 'Messages Opened'
    )
    messages_engaged = Field(
        attribute = 'messages-engaged',
        column_name = 'Messages Engaged'
    )

    class Meta:
        export_order = [
            'date',
            'app_page_views',
            'app_used',
            'fitbit_minutes_worn',
            'fitbit_step_count',
            'fitbit_updated',
            'fitbit_updated_completely',
            'fitbit_worn',
            'location_count',
            'messages_sent',
            'messages_received',
            'messages_opened',
            'messages_engaged'
        ]
    
    def dehydrate_date(self, instance):
        if instance.date:
            return instance.date.strftime('%Y-%m-%d')
        return None

def export_adherence_metrics(username, directory=None, filename=None, start_date=None, end_date=None):
    if not filename:
        filename = '%s.adherence_metrics.csv' % (username)
    if not directory:
        directory = './'
    try:
        adherence_service = AdherenceService(username = username)
    except AdherenceService.NoConfiguration:
        return False
    days = Day.objects.filter(user__username=username).all()
    if not start_date:
        start_date = days[0].date
    if not end_date:
        end_date = days[len(days)-1].date

    page_views_by_date = {}
    page_views = PageView.objects.filter(
        user__username = username
    ).order_by('time').all()
    page_views = list(page_views)
    for _day in days:
        page_view_count = 0
        while page_views and page_views[0].time < _day.start:
            page_views.pop(0)
        while page_views and page_views[0].time < _day.end:
            page_view_count += 1
            page_views.pop(0)
        page_views_by_date[_day.date] = page_view_count

    locations_by_date = {}
    locations = Location.objects.filter(
        user__username = username
    ).order_by('time').all()
    locations = list(locations)
    for _day in days:
        locations_count = 0
        while locations and locations[0].time < _day.start:
            locations.pop(0)
        while locations and locations[0].time < _day.end:
            locations.pop(0)
            locations_count += 1
        locations_by_date[_day.date] = locations_count

    messages_by_date = {}
    messages = Message.objects.filter(
        recipient__username = username
    ).order_by('created').all()
    messages = list(messages)
    for _day in days:
        messages_sent_count = 0
        messages_received_count = 0
        messages_opened_count = 0
        messages_engaged_count = 0
        while messages and messages[0].created < _day.end:
            _message = messages.pop(0)
            if _message.sent:
                messages_sent_count += 1
            if _message.received:
                messages_received_count += 1
            if _message.opened:
                messages_opened_count += 1
            if _message.engaged:
                messages_engaged_count += 1
        messages_by_date[_day.date] = {
            'sent': messages_sent_count,
            'received': messages_received_count,
            'opened': messages_opened_count,
            'engaged': messages_engaged_count
        }

    fitbit_activity_by_date = {}
    try:
        fitbit_service = FitbitService(username=username)
        fitbit_account = fitbit_service.account
        fitbit_days = FitbitDay.objects.filter(
            account = fitbit_account
        ).all()
        for _fitbit_day in fitbit_days:
            fitbit_activity_by_date[_fitbit_day.date] = {
                'step_count': _fitbit_day.step_count,
                'completely_updated': _fitbit_day.completely_updated,
                'minutes_worn': _fitbit_day.minutes_worn
            }
    except FitbitService.NoAccount:
        pass

    daily_adherence_by_date = {}
    for metric in AdherenceMetric.objects.order_by('date').filter(user__username=username).all():
        if metric.date not in daily_adherence_by_date:
            daily_adherence_by_date[metric.date] = {}
        daily_adherence_by_date[metric.date][metric.category] = metric.value
    
    first_day = days[0]
    last_day = days[len(days) - 1]
    date_range = (last_day.date - first_day.date).days
    all_dates = [first_day.date + timedelta(days=offset) for offset in range(date_range)]
    
    days = []
    for _date in all_dates:
        daily_adherence = DailyAdherence(_date)
        daily_adherence.date = _date
        if _date in daily_adherence_by_date:
            for _key, _value in daily_adherence_by_date[_date].items():
                setattr(daily_adherence, _key, _value)
        if _date in page_views_by_date:
            daily_adherence.app_page_views = page_views_by_date[_date]
        if _date in locations_by_date:
            daily_adherence.location_count = locations_by_date[_date]
        if _date in messages_by_date:
            for _key, _value in messages_by_date[_date].items():
                setattr(daily_adherence, 'messages-%s' % (_key), _value)
        if _date in fitbit_activity_by_date:
            setattr(daily_adherence, 'fitbit_minutes_worn', fitbit_activity_by_date[_date]['minutes_worn'])
            setattr(daily_adherence, 'fitbit_step_count', fitbit_activity_by_date[_date]['step_count'])
            setattr(daily_adherence, 'fitbit-updated-completely', fitbit_activity_by_date[_date]['completely_updated'])
        days.append(daily_adherence)

    dataset = DailyAdherenceResource().export(queryset=days)
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
