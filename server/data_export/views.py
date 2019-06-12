from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from .resources import *

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def export_table(request, export_table):
    export_resource = create_resource(export_table)
    if export_resource in EXCEPTION_FOUND:
        response = HttpResponse(export_resource)
    else:
        dataset = export_resource().export()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{export_table}.csv"'
    return response
