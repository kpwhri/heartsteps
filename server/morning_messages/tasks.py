from datetime import date
from datetime import timedelta
from os import path
import csv

from celery import shared_task

from days.services import DayService
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

def export_morning_messages(username, filename=None, directory=None, start=None, end=None):
    user = User.objects.get(username=username)
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.morning_messages.csv' % (username)

    morning_message_query = MorningMessage.objects \
        .order_by('date') \
        .filter(
            user = user
        ) \
        .prefetch_decision() \
        .prefetch_message_template() \
        .prefetch_message() \
        .prefetch_timezone()
    if start:
        day_service = DayService(user=user)
        start_date = day_service.get_date_at(start)
        morning_message_query = morning_message_query.filter(
            date__gte=start_date
        )
    if end:
        day_service = DayService(user=user)
        end_date = day_service.get_date_at(end)
        morning_message_query = morning_message_query.filter(
            date__lte=end_date
        )

    morning_messages = morning_message_query.all()
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
            morning_message_template_id = None
            if morning_message.message_template:
                morning_message_template_id = morning_message.message_template.id        
            rows.append([
                morning_message.date.strftime('%Y-%m-%d'),
                time_sent,
                time_received,
                time_opened,
                time_completed,
                morning_message.notification,
                morning_message_template_id,
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


def export_morning_message_survey(username, filename=None, directory=None, start=None, end=None):
    user = User.objects.get(username=username)
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.morning-survey.csv' % (username)

    morning_message_query = MorningMessage.objects \
        .order_by('date') \
        .filter(
            user = user
        ) \
        .prefetch_decision() \
        .prefetch_message() \
        .prefetch_survey() \
        .prefetch_timezone()
    if start:
        day_service = DayService(user=user)
        start_date = day_service.get_date_at(start)
        morning_message_query = morning_message_query.filter(
            date__gte=start_date
        )
    if end:
        day_service = DayService(user=user)
        end_date = day_service.get_date_at(end)
        morning_message_query = morning_message_query.filter(
            date__lte=end_date
        )
    morning_messages = morning_message_query.all()

    question_names = []
    serialized_morning_messages_by_date = {}
    for morning_message in morning_messages:
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
        _mm_serialized = {
            'time_sent': time_sent,
            'time_received': time_received,
            'time_opened': time_opened,
            'time_completed': time_completed
        }
        if morning_message.survey and morning_message.survey.answered and morning_message.survey._questions:
            for question in morning_message.survey.questions:
                if question.name not in question_names:
                    question_names.append(question.name)
                if question.id in morning_message.survey._answers:
                    answer = morning_message.survey._answers[question.id]
                    _mm_serialized[question.name] = answer.value
            _mm_serialized['mood'] = morning_message.survey.selected_word
        serialized_morning_messages_by_date[morning_message.date] = _mm_serialized

    sorted_question_names = sorted(question_names)

    rows = []
    headers = [
        'Date',
        'Time Sent',
        'Time Received',
        'Time Opened',
        'Time Completed',
    ] + [_name.title() for _name in sorted_question_names] + [
        'Mood'
    ]
    rows.append(headers)

    start_date = morning_messages[0].date
    end_date = morning_messages[len(morning_messages) - 1].date
    date_diff = end_date - start_date
    for _date in [start_date + timedelta(days=offset) for offset in range(date_diff.days)]:
        if _date in serialized_morning_messages_by_date:
            _mm = serialized_morning_messages_by_date[_date]
            row = [
                _date.strftime('%Y-%m-%d'),
                _mm['time_sent'],
                _mm['time_received'],
                _mm['time_opened'],
                _mm['time_completed']
            ]
            for name in sorted_question_names:
                if name in _mm:
                    row.append(_mm[name])
                else:
                    row.append(None)
            if 'mood' in _mm:
                row.append(_mm['mood'])
            else:
                row.append(None)
            rows.append(row)
        else:
            rows.append([
                _date.strftime('%Y-%m-%d')
            ])

    _file = open(path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(rows)
    _file.close()
