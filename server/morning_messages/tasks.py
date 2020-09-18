from datetime import date
from datetime import timedelta
from os import path
import csv

from celery import shared_task

from .models import MorningMessage
from .models import User
from .services import MorningMessageService

@shared_task
def send_morning_message(username):
    service = MorningMessageService(username=username)
    try:
        service.send_notification(date.today())
    except MorningMessageService.NotEnabled:
        pass

@shared_task
def export_morning_messages(username, filename=None, directory=None):
    user = User.objects.get(username=username)
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.morning_messages.csv' % (username)

    morning_messages = MorningMessage.objects \
        .order_by('date') \
        .filter(
            user = user
        ) \
        .prefetch_decision() \
        .prefetch_message() \
        .prefetch_survey() \
        .prefetch_timezone() \
        .all()
    start_date = morning_messages[0].date
    end_date = morning_messages[len(morning_messages) - 1].date
    date_diff = end_date - start_date
    every_day = [start_date + timedelta(days=offset) for offset in range(date_diff.days)]
    
    rows = []
    headers = [
        'Date',
        'Time Sent',
        'Time Received',
        'Time Opened',
        'Time Completed',
        'Notification',
        'Morning Message ID',
        'Morning Message',
        'Anchor Message',
        'Gain Frame',
        'Loss Frame',
        'Active Frame',
        'Sedentary Frame'
    ]
    rows.append(headers)

    morning_messages_by_date = {}
    for morning_message in morning_messages:
        morning_messages_by_date[morning_message.date] = morning_message

    for _date in every_day:
        if _date in morning_messages_by_date:
            morning_message = morning_messages_by_date[_date]
            time_sent = None
            time_received = None
            time_opened = None
            time_completed = None
            if morning_message.message:
                _tz = morning_message.timezone
                if morning_message.message.sent:
                    time_sent = morning_message.message.sent.astimezone(_tz).strftime('%Y-%m-%d %H:%M:%s')
                if morning_message.message.received:
                    time_received = morning_message.message.received.astimezone(_tz).strftime('%Y-%m-%d %H:%M:%s')
                if morning_message.message.opened:
                    time_opened = morning_message.message.opened.astimezone(_tz).strftime('%Y-%m-%d %H:%M:%s')
                if morning_message.message.engaged:
                    time_completed = morning_message.message.engaged.astimezone(_tz).strftime('%Y-%m-%d %H:%M:%s')        
            rows.append([
                morning_message.date.strftime('%Y-%m-%d'),
                time_sent,
                time_received,
                time_opened,
                time_completed,
                morning_message.notification,
                '???',
                morning_message.text,
                morning_message.anchor,
                morning_message.is_gain_framed,
                morning_message.is_loss_framed,
                morning_message.is_active_framed,
                morning_message.is_sedentary_framed
            ])
        else:
            rows.append([
                _date.strftime('%Y-%m-%d')
            ])

    
    _file = open(path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(rows)
    _file.close()
