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
    date = None
    app_page_views = 0

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

    fitbit_worn = Field(
        attribute = 'fitbit-worn',
        column_name = 'Fitbit Worn'
    )
    fitbit_updated = Field(
        attribute = 'fitbit-updated',
        column_name = 'Fitbit Updated'
    )

    class Meta:
        export_order = [
            'date',
            'app_page_views',
            'app_used',
            'fitbit_updated',
            'fitbit_worn'
        ]
    
    def dehydrate_date(self, instance):
        if instance.date:
            return instance.date.strftime('%Y-%m-%d')
        return None

def make_timezone_list(days):
    timezone_list = []
    _timezone = None
    for _day in days:
        if _day.timezone != _timezone:
            _timezone = _day.timezone
            timezone_list.append({
                'timezone': _day.get_timezone(),
                'start_datetime': _day.start
            })
    return timezone_list

def export_adherence_metrics(username, directory=None, filename=None):
    if not filename:
        filename = '%s.adherence_metrics.csv' % (username)
    if not directory:
        directory = './'
    try:
        adherence_service = AdherenceService(username = username)
    except AdherenceService.NoConfiguration:
        return False

    days = Day.objects.filter(user__username=username).all()

    
    page_views_by_date = {}
    page_views = PageView.objects.filter(
        user__username = username
    ).all()
    timezone_list = make_timezone_list(days)
    _timezone = pytz.UTC
    if len(timezone_list):
        _timezone = timezone_list.pop(0)['timezone']
    for _page_view in page_views:
        if len(timezone_list):
            next_timezone_start = timezone_list[0]['start_datetime']
            while _page_view.time <= next_timezone_start and len(timezone_list):
                _tz = timezone_list.pop(0)
                next_timezone_start = _tz['start_datetime']
                _timezone = _tz['timezone']
        page_view_datetime = _page_view.time.astimezone(_timezone)
        page_view_date = date(page_view_datetime.year,page_view_datetime.month, page_view_datetime.day)
        if page_view_date not in page_views_by_date:
            page_views_by_date[page_view_date] = 1
        else:
            page_views_by_date[page_view_date] += 1
    print(page_views_by_date.values())

    daily_adherence_by_date = {}
    for metric in AdherenceMetric.objects.order_by('date').filter(user__username=username).all():
        if metric.date not in daily_adherence_by_date:
            daily_adherence_by_date[metric.date] = DailyAdherence()
            daily_adherence_by_date[metric.date].date = metric.date
        setattr(daily_adherence_by_date[metric.date], metric.category, metric.value)
    
    first_day = days[0]
    last_day = days[len(days) - 1]
    date_range = (last_day.date - first_day.date).days
    all_dates = [first_day.date + timedelta(days=offset) for offset in range(date_range)]
    
    days = []
    for _date in all_dates:
        daily_adherence = None
        if _date in daily_adherence_by_date:
            daily_adherence = daily_adherence_by_date[_date]
        else:
            daily_adherence = DailyAdherence()
            daily_adherence.date = _date
        if _date in page_views_by_date:
            daily_adherence.app_page_views = page_views_by_date[_date]
        days.append(daily_adherence)

    dataset = DailyAdherenceResource().export(queryset=days)
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
