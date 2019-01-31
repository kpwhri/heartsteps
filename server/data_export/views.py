from django.http import HttpResponse
from .resources import *

# allowed_tables = {
#     "activity_logs":        "activity_log",
#     "activity_logs":        "activity_log_source",
#     "anti_seds":            "step_count"
# }

# table_whitelist = {
#     "activity_log_source":  ActivityLogSourceResource,
#     "step_count":           StepCountResource
# }

# def fabric(baseclass=resources.ModelResource):
#     for table in table_whitelist:
#         print(table)
#         print(table_whitelist[table])
#         class Meta:
#             model = StepCount # This has to be dynamic
#         attrs = {'__module__': baseclass.__module__, 'Meta': Meta}
#         newclass = type(str(table_whitelist[table]), (baseclass,), attrs)
#         globals()[table_whitelist[table]] = newclass

# def export_table(request, export_table):
#     # fabric()
#     # export_resource = table_whitelist[export_table]()
#     dataset = export_resource.export()
#     response = HttpResponse(dataset.csv, content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="{export_table}.csv"'
#     return response

def export_step_count(request):
    export_resource = StepCountResource
    dataset = export_resource().export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="step_count.csv"'
    return response
