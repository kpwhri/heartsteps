import csv
from datetime import timedelta

from days.services import DayService

from .models import StepCount

def export_step_count_records_csv(users, filename, start_date, end_date):
    dates_diff = end_date - start_date
    dates = [start_date + timedelta(days=offset) for offset in range(dates_diff.days)]

    rows = []
    for _user in users:
        row = [_user.username]
        day_service = DayService(user=_user)
        for _date in dates:
            start = day_service.get_start_of_day(_date)
            end = start + timedelta(days=1)
            if _user.date_joined < end:
                query = StepCount.objects.filter(
                    user = _user,
                    start__range = [start, end]
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
