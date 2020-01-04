from celery import shared_task

from fitbit_activities.services import FitbitActivityService


@shared_task
def update_fitbit_data(fitbit_user, date_string):
    service = FitbitActivityService(
        fitbit_user = fitbit_user,
    )
    date = service.parse_date(date_string)
    service.update(date)
