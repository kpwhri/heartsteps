import os
from celery import shared_task
import csv
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from import_export import resources
from import_export.fields import Field

from fitbit_api.services import FitbitClient
from fitbit_api.models import FitbitAccountUser

from .models import FitbitAccount
from .models import FitbitDay
from .services import FitbitActivityService


@shared_task
def update_fitbit_data(fitbit_user, date_string):
    service = FitbitActivityService(
        fitbit_user = fitbit_user,
    )
    service.update_devices()
    date = service.parse_date(date_string)
    service.update(date)

@shared_task
def update_incomplete_days(fitbit_user):
    try:
        service = FitbitActivityService(
            fitbit_user = fitbit_user
        )
        query = FitbitDay.objects.filter(
            account = service.account,
            completely_updated = False
        ).order_by('date')
        for day in query.all():
            service.update(day.date)
    except FitbitClient.Unauthorized:
        pass
    except FitbitClient.TooManyRequests:
        update_incomplete_days.apply_async(
            eta = timezone.now() + timedelta(minutes=90),
            kwargs = {
                'fitbit_user': fitbit_user
            }
        )

@shared_task
def update_all_fitbit_data(fitbit_user):
    service = FitbitAccount(fitbit_user = fitbit_user)
    FitbitDay.objects.filter(
        account = account
    ).update(
        completely_updated = False
    )
    update_incomplete_days.apply_async(kwargs={
        'fitbit_user': fitbit_user
    })



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

def export_fitbit_data(username, directory = None, filename = None, start=None, end=None):
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.fitbit_minutes.csv'.format(
            username = username
        )
    fitbit_service = FitbitActivityService(username=username)
    fitbit_account = fitbit_service.account

    minute_level_data = []

    class MinuteLevelData:
        username = None
        fitbit_account = None
        timezone = None
        date = None
        time = None
        steps = None
        heart_rate = None

    days_by_date = {}
    for fitbit_day in FitbitDay.objects.filter(account=fitbit_account).all():
        if start and start >= fitbit_day.get_end_datetime():
            continue
        if end and end <= fitbit_day.get_start_datetime():
            continue
        days_by_date[fitbit_day.date] = fitbit_day

    if not days_by_date:
        raise 'No fitbit days exist for user'

    dates = sorted(list(days_by_date.keys()))
    date_range = (dates[-1] - dates[0]).days
    all_days = [dates[0] + timedelta(days=offset) for offset in range(date_range)]

    for _date in all_days:
        if _date in days_by_date:
            day = days_by_date[_date]
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
        else:
            start_datetime = datetime(_date.year, _date.month, _date.day, 0, 0, 0)
            end_datetime = start_datetime + timedelta(days=1)
            current_minute = start_datetime
            while current_minute < end_datetime:
                _m = MinuteLevelData()
                _m.username = username,
                _m.fitbit_account = fitbit_account.fitbit_user,
                _m.timezone = day._timezone,
                _m.date = current_minute.strftime('%Y-%m-%d')
                _m.time = current_minute.strftime('%H:%M:S')
                minute_level_data.append(_m)
                current_minute = current_minute + timedelta(minutes=1)
    
    dataset = FitbitMinuteDataResource().export(minute_level_data)

    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()

def export_missing_fitbit_data(users, filename=None, directory=None, start=None, end=None):
    if not filename:
        filename = 'incomplete_fitbit_data.csv'
    if not directory:
        directory = './'
    usernames = [u.username for u in users]
    account_user_query = FitbitAccountUser.objects.filter(
        user__username__in=usernames
    ).prefetch_related('user').prefetch_related('account')
    accounts = []
    username_by_fitbit_account = {}
    account_id_by_username = {}        
    for au in account_user_query.all():
        username_by_fitbit_account[au.account.fitbit_user] = au.user.username
        account_id_by_username[au.user.username] = au.account.fitbit_user
        if au.account not in accounts:
            accounts.append(au.account)
    account_ids = [account.fitbit_user for account in accounts]
    complete_data_dates = {}
    days = FitbitDay.objects.filter(account__fitbit_user__in=account_ids).prefetch_related('account').all()
    all_dates = []
    for _day in days:
        account_id = _day.account.fitbit_user
        if account_id not in complete_data_dates:
            complete_data_dates[account_id] = {}
        complete_data_dates[account_id][_day.date] = _day.completely_updated
        if _day.date not in all_dates:
            all_dates.append(_day.date)
    sorted_usernames = sorted(usernames)
    sorted_dates = sorted(all_dates)
    rows = []
    header = [''] + [_d.strftime('%Y-%m-%d') for _d in sorted_dates]
    rows.append(header)
    for username in sorted_usernames:
        _row = [username]
        if username in account_id_by_username:
            account_id = account_id_by_username[username]
            if account_id in complete_data_dates:
                for _date in sorted_dates:
                    if _date in complete_data_dates[account_id]:
                        if complete_data_dates[account_id][_date]:
                            _row.append(1)
                        else:
                            _row.append(0)
                    else:
                        _row.append('')
        rows.append(_row)
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(rows)
    _file.close()
