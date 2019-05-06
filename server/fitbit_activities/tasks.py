from celery import shared_task

from fitbit_activities.services import FitbitDayService, parse_fitbit_date


@shared_task
def update_fitbit_data(fitbit_user, date_string):
    fitbit_day = FitbitDayService(
        fitbit_user = fitbit_user,
        date = parse_fitbit_date(date_string)
    )
    fitbit_day.update()
