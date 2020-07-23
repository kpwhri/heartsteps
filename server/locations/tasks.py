import csv
from datetime import datetime
from datetime import timedelta
import pytz
from celery import shared_task

from .models import Location
from .services import LocationService

@shared_task
def update_location_categories(username):
    service = LocationService(
        username=username
    )
    locations = Location.objects.filter(
        user__username = username,
        category = None
    )
    for location in locations.all():
        location.category = service.categorize_location(
            latitude = location.latitude,
            longitude = location.longitude
        )
        location.save()

def export_location_count_csv(users, filename, start_date, end_date, ignore_null_island=True):
    dates_diff = end_date - start_date
    dates = [start_date + timedelta(days=offset) for offset in range(dates_diff.days)]

    rows = []
    for _user in users:
        row = [_user.username]
        for _date in dates:
            start = datetime(_date.year, _date.month, _date.day, tzinfo=pytz.UTC)
            end = start + timedelta(days=1)
            if _user.date_joined < end:
                query = Location.objects.filter(
                    user = _user,
                    time__range = [start, end]
                )
                if ignore_null_island:
                    query = query.exclude(
                        latitude=0.0,
                        longitude=0.0
                    )
                row.append(query.count())
            else:
                row.append(None)
        rows.append(row)
    
    headers = [''] + [d.strftime('%Y-%m-%d') for d in dates]
    rows = [headers] + rows
    f = open(filename, 'w')
    writer = csv.writer(f)
    writer.writerows(rows)
    f.close()
