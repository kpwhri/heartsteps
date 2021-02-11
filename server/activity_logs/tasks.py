from datetime import date
from datetime import timedelta
from os import path
import csv
import pytz

from days.services import DayService

from .models import ActivityLog


def export_activity_logs(username, filename=None, directory=None, start=None, end=None):
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.activity_logs.csv' % (username)

    activity_log_query = ActivityLog.objects.filter(
        user__username=username
    ) \
    .order_by('start') \
    .prefetch_related('type')

    day_service = DayService(username=username)
    if start:
        start_datetime = day_service.get_start_of_day(start)
        activity_log_query = activity_log_query.filter(
            start__gte=start_datetime
        )
    if end:
        end_datetime = day_service.get_end_of_day(end)
        activity_log_query = activity_log_query.filter(
            start__lte=end_datetime
        )

    rows = []
    headers = [
        'Participant ID',
        'Activity ID',
        'Study Day',
        'Date',
        'Start Time',
        'Timezone',
        'Activity Type ID',
        'Activity Type Title',
        'Activity Duration',
        'Activity Vigorous'
    ]
    rows.append(headers)

    for activity_log in activity_log_query.all():
        rows.append([
            username,
            activity_log.id,
            'study day',
            activity_log.start.astimezone(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d'),
            activity_log.start.astimezone(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S'),
            'timezone',
            activity_log.type.id,
            activity_log.type.title,
            activity_log.duration,
            activity_log.vigorous
        ])

    _file = open(path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(rows)
    _file.close()




