import csv
import os
from datetime import datetime
from import_export import resources
from import_export.fields import Field

from days.models import Day
from service_requests.admin import ServiceRequestResource

from .admin import AntiSedentaryDecisionResouce
from .models import AntiSedentaryDecision
from .models import AntiSedentaryServiceRequest


def export_anti_sedentary_decisions(username, directory=None, filename=None, start=None, end=None):
    if not filename:
        filename = '%s.anti_sedentary_decisions.csv' % (username)
    if not directory:
        directory = './'
    
    queryset = AntiSedentaryDecision.objects.filter(
        user__username=username,
        test = False
    ) \
    .order_by('time') \
    .prefetch_rating() \
    .prefetch_weather_forecast() \
    .prefetch_location() \
    .prefetch_notification() \
    .prefetch_unavailable_reasons() \
    .prefetch_message_template(AntiSedentaryDecision.MESSAGE_TEMPLATE_MODEL)

    if start:
        queryset = queryset.filter(time__gte = start)
    if end:
        queryset = queryset.filter(time__lte = end)
    
    total_rows = queryset.count()
    _file = open(os.path.join(directory, filename), 'w')
    start_index = 0
    slice_size = 100
    first = True
    while start_index < total_rows:
        end_index = start_index + slice_size
        if end_index >= total_rows:
            end_index = total_rows - 1

        decisions = queryset[start_index:end_index]
        if decisions:
            earliest_decision_time = None
            latest_decision_time = None
            for _decision in decisions:
                if not earliest_decision_time or _decision.time < earliest_decision_time:
                    earliest_decision_time = _decision.time
                if not latest_decision_time or _decision.time > latest_decision_time:
                    latest_decision_time = _decision.time
            days = Day.objects.filter(
                start__lte = latest_decision_time,
                end__gte = earliest_decision_time,
                user__username = username
            ).all()
            new_decisions = []
            for decision in decisions:
                for _day in days:
                    if decision.time > _day.start and decision.time < _day.end:
                        decision._timezone = _day.get_timezone()
                        continue
                new_decisions.append(decision)

            dataset = AntiSedentaryDecisionResouce().export(
                queryset = new_decisions
            )
            csv = dataset.csv
            if first:
                first = False
            else:
                csv_list = csv.split('\r\n')
                csv = '\r\n'.join(csv_list[1:])
            _file.write(csv)
        start_index = start_index + slice_size
    _file.close()

def export_anti_sedentary_service_requests(username, directory=None, filename=None, start=None, end=None):
    if not filename:
        filename = '%s.anti_sedentary_service_requests.csv' % (username)
    if not directory:
        directory = './'

    queryset = AntiSedentaryServiceRequest.objects.filter(
        user__username = username
    )
    if start:
        queryset = queryset.filter(request_time__gte=start)
    if end:
        queryset = queryset.filter(request_time__lte=end)

    dataset = ServiceRequestResource().export(
        queryset = queryset
    )
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
