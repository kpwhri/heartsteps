import csv
import os
from import_export import resources
from import_export.fields import Field

from service_requests.admin import ServiceRequestResource

from .admin import AntiSedentaryDecisionResouce
from .models import AntiSedentaryDecision
from .models import AntiSedentaryServiceRequest


def export_anti_sedentary_decisions(username, directory):
    queryset = AntiSedentaryDecision.objects.filter(user__username=username)
    total_rows = queryset.count()
    filename = '%s.anti_sedentary_decisions.csv' % (username)
    _file = open(os.path.join(directory, filename), 'w')
    start_index = 0
    slice_size = 100
    first = True
    while start_index < total_rows:
        end_index = start_index + slice_size
        if end_index >= total_rows:
            end_index = total_rows - 1
        dataset = AntiSedentaryDecisionResouce().export(
            queryset = queryset[start_index:end_index]
        )
        csv = dataset.csv
        if first:
            first = False
        else:
            csv_list = csv.split('\r\n')
            csv = '\r\n'.join(csv_list[1:])
        _file.write(dataset.csv)
        start_index = start_index + slice_size
    _file.close()

def export_anti_sedentary_service_requests(username, directory):
    dataset = ServiceRequestResource().export(
        queryset = AntiSedentaryServiceRequest.objects.filter(
            user__username = username
        )
    )
    filename = '%s.anti_sedentary_service_requests.csv' % (username)
    _file = open(os.path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
