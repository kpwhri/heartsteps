from celery import shared_task
from datetime import timedelta
from import_export import resources
from import_export.fields import Field
import os

from days.models import Day
from locations.models import Location
from fitbit_activities.models import FitbitDay
from fitbit_api.services import FitbitService
from fitbit_api.models import FitbitSubscriptionUpdate
from fitbit_api.models import FitbitAccountUpdate
from push_messages.models import Message
from page_views.models import PageView

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
        attribute = 'app_used',
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
        attribute = 'fitbit_worn',
        column_name = 'Fitbit Worn'
    )
    fitbit_update_count = Field(
        attribute = 'fitbit_update_count',
        column_name = 'Fitbit Update Count'
    )
    fitbit_updated_completely = Field(
        attribute = 'fitbit_updated_completely',
        column_name = 'Fitbit Updated Completely'
    )
    location_count = Field(
        attribute = 'location_count',
        column_name = 'Number of Location Records'
    )
    messages_sent = Field(
        attribute = 'messages_sent',
        column_name = 'Messages Sent'
    )
    messages_received = Field(
        attribute = 'messages_received',
        column_name = 'Messages Received'
    )
    messages_opened = Field(
        attribute = 'messages_opened',
        column_name = 'Messages Opened'
    )
    messages_engaged = Field(
        attribute = 'messages_engaged',
        column_name = 'Messages Engaged'
    )

    class Meta:
        export_order = [
            'date',
            'app_page_views',
            'app_used',
            'fitbit_minutes_worn',
            'fitbit_step_count',
            'fitbit_update_count',
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

def get_page_views_by_date(username, days):
    page_views_by_date = {}
    page_views = PageView.objects.filter(
        user__username = username,
        time__gte = days[0].start,
        time__lte = days[-1].end
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
    return page_views_by_date

def get_locations_by_date(username, days):
    locations_by_date = {}
    locations = Location.objects.filter(
        user__username = username,
        time__gte = days[0].start,
        time__lte = days[-1].end
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
    return locations_by_date

def get_messages_by_date(username, days):
    messages_by_date = {}
    messages = Message.objects.filter(
        recipient__username = username,
        created__gte = days[0].start,
        created__lte = days[-1].end
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
    return messages_by_date

def get_fitbit_activity_by_date(username, days):
    fitbit_activity_by_date = {}
    for day in days:
        fitbit_activity_by_date[day.date] = {
            'step_count': 0,
            'completely_updated': 0,
            'wore_fitbit': 0,
            'minutes_worn': 0,
            'update_count': 0
        }
    try:
        fitbit_service = FitbitService(username=username)
        fitbit_account = fitbit_service.account
        fitbit_days = FitbitDay.objects.filter(
            account = fitbit_account,
            date__gte = days[0].date,
            date__lte = days[-1].date
        ).all()
        for _fitbit_day in fitbit_days:
            fitbit_activity_by_date[_fitbit_day.date]['step_count'] = _fitbit_day.step_count
            fitbit_activity_by_date[_fitbit_day.date]['completely_updated'] = _fitbit_day.completely_updated
            fitbit_activity_by_date[_fitbit_day.date]['wore_fitbit'] = _fitbit_day.wore_fitbit
            fitbit_activity_by_date[_fitbit_day.date]['minutes_worn'] = _fitbit_day.minutes_worn
        
        account_updates = FitbitAccountUpdate.objects.filter(
            account=fitbit_account
        ).order_by('created') \
        .all()
        subscription_updates = FitbitSubscriptionUpdate.objects.filter(
            subscription__fitbit_account=fitbit_account
        ).order_by('created') \
        .all()

        account_activity = list(account_updates) + list(subscription_updates)
        account_activity.sort(key=lambda x: x.created)
        for day in days:
            count = 0
            while account_activity and account_activity[0].created >= day.start and account_activity[0].created <= day.end:
                account_activity.pop(0)
                count += 1
            fitbit_activity_by_date[day.date]['update_count'] = count
        
    except FitbitService.NoAccount:
        pass
    return fitbit_activity_by_date


def export_daily_metrics(username, directory=None, filename=None, start=None, end=None):
    if not filename:
        filename = '%s.daily_metrics.csv' % (username)
    if not directory:
        directory = './'
    
    days_query = Day.objects.filter(user__username=username)
    if start:
        days_query = days_query.filter(start__gte=start)
    if end:
        days_query = days_query.filter(end__lte=end)
    days = list(days_query.all())
    
    if not days:
        raise RuntimeError('No days exist for user')

    first_date = days[0].date
    last_date = days[-1].date
    date_range = (last_date - first_date).days
    all_dates = [first_date + timedelta(days=offset) for offset in range(date_range)]

    page_views_by_date = get_page_views_by_date(username, days)
    locations_by_date = get_locations_by_date(username, days)
    messages_by_date = get_messages_by_date(username, days)
    fitbit_activity_by_date = get_fitbit_activity_by_date(username, days)

    daily_adherence_metrics = []
    for _date in all_dates:
        daily_adherence = DailyAdherence(_date)
        if _date in page_views_by_date:
            daily_adherence.app_page_views = page_views_by_date[_date]
            if daily_adherence.app_page_views > 0:
                daily_adherence.app_used = True
            else:
                daily_adherence.app_used = False
        if _date in locations_by_date:
            daily_adherence.location_count = locations_by_date[_date]
        if _date in messages_by_date:
            for _key, _value in messages_by_date[_date].items():
                setattr(daily_adherence, 'messages_%s' % (_key), _value)
        if _date in fitbit_activity_by_date:
            daily_adherence.fitbit_worn = fitbit_activity_by_date[_date]['wore_fitbit']
            daily_adherence.fitbit_minutes_worn = fitbit_activity_by_date[_date]['minutes_worn']
            daily_adherence.fitbit_step_count = fitbit_activity_by_date[_date]['step_count']
            daily_adherence.fitbit_updated_completely = fitbit_activity_by_date[_date]['completely_updated']
            daily_adherence.fitbit_update_count = fitbit_activity_by_date[_date]['update_count']
        daily_adherence_metrics.append(daily_adherence)

    dataset = DailyAdherenceResource().export(queryset=daily_adherence_metrics)
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
