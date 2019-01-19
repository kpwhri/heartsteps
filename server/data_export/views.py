from django.http import HttpResponse
from .resources import StepCountResource

def export_step_count(request):
    step_count_resource = StepCountResource()
    dataset = step_count_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="step_counts.csv"'
    return response
