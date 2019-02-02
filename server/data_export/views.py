from django.http import HttpResponse
from .resources import *

# Create the django-import-export resource & instantialize
def export_table(request, export_table):
    export_resource = create_resource(export_table)
    if export_resource == MODEL_NOT_FOUND:
        response = HttpResponse(MODEL_NOT_FOUND)
    else:
        dataset = export_resource().export()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{export_table}.csv"'
    return response
