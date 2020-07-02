from datetime import date
from datetime import timedelta
from os import path

from celery import shared_task

from .models import MorningMessage
from .models import User
from .resources import MorningMessageResource
from .services import MorningMessageService

@shared_task
def send_morning_message(username):
    service = MorningMessageService(username=username)
    try:
        service.send_notification(date.today())
    except MorningMessageService.NotEnabled:
        pass

@shared_task
def export_morning_messages(username, directory):
    user = User.objects.get(username=username)
    filename = '%s.morning_messages.csv' % (username)
    _file = open(path.join(directory, filename), 'w')

    morning_messages = MorningMessage.objects \
        .order_by('date') \
        .filter(
            user = user
        ) \
        .all()
    start_date = morning_messages[0].date
    end_date = morning_messages[len(morning_messages) - 1].date
    date_diff = end_date - start_date
    every_day = [start_date + timedelta(days=offset) for offset in range(date_diff.days)]
    
    morning_message_dict = {}
    for _morning_message in morning_messages:
        morning_message_dict[_morning_message.date] = _morning_message
    
    every_morning_message = []
    for _date in every_day:
        if _date in morning_message_dict:
            every_morning_message.append(morning_message_dict[_date])
        else:
            unsaved_morning_message = MorningMessage(
                user = user,
                date = _date
            )
            every_morning_message.append(unsaved_morning_message)

    dataset = MorningMessageResource().export(
        queryset = every_morning_message
    )
    
    _file.write(dataset.csv)
    _file.close()
