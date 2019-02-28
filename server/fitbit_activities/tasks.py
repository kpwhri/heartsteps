from celery import shared_task

from fitbit_activities.services import FitbitDayService, parse_fitbit_date


@shared_task
def update_fitbit_data(username, date_string):
    fitbit_day = FitbitDayService(
        username = username,
        date = parse_fitbit_date(date_string)
    )
    fitbit_day.update()
