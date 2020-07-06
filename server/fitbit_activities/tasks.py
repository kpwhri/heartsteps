from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from import_export import resources
from import_export.fields import Field

from fitbit_api.services import FitbitClient

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
            day.update(day.date)
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

def export_fitbit_data(username, directory):
    fitbit_service = FitbitActivityService(username=username)
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

    filename = '%s.fitbit_minutes.csv' % (username)
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()

