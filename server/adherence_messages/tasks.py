from celery import shared_task
from datetime import timedelta
from import_export import resources
from import_export.fields import Field
import os

from anti_sedentary.models import AntiSedentaryDecision
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
    app_page_views = None
    app_used = None
    fitbit_worn = None
    fitbit_updated = None

class DailyAdherenceResource(resources.Resource):
    date = Field(column_name='Date')

    app_used = Field(
        attribute = 'app-used',
        column_name = 'App Used'
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
            'app_used',
            'fitbit_updated',
            'fitbit_worn'
        ]
    
    def dehydrate_date(self, instance):
        if instance.date:
            return instance.date.strftime('%Y-%m-%d')
        return None

def export_adherence_metrics(username, directory=None, filename=None):
    if not filename:
        filename = '%s.adherence_metrics.csv' % (username)
    if not directory:
        directory = './'
    try:
        adherence_service = AdherenceService(username = username)
    except AdherenceService.NoConfiguration:
        return False
    
    daily_adherence_by_date = {}
    for metric in AdherenceMetric.objects.order_by('date').filter(user__username=username).all():
        if metric.date not in daily_adherence_by_date:
            daily_adherence_by_date[metric.date] = DailyAdherence()
            daily_adherence_by_date[metric.date].date = metric.date
        setattr(daily_adherence_by_date[metric.date], metric.category, metric.value)
    
    adherence_dates_sorted = sorted(daily_adherence_by_date.keys())
    first_date = adherence_dates_sorted[0]
    last_date = adherence_dates_sorted[len(adherence_dates_sorted) - 1]
    date_range = (last_date - first_date).days
    all_dates = [first_date + timedelta(days=offset) for offset in range(date_range)]
    
    days = []
    for _date in all_dates:
        if _date in daily_adherence_by_date:
            days.append(daily_adherence_by_date[_date])
        else:
            daily_adherence = DailyAdherence()
            daily_adherence.date = _date
            days.append(daily_adherence)

    dataset = DailyAdherenceResource().export(queryset=days)
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
