from import_export import resources
from anti_seds.models import StepCount

class StepCountResource(resources.ModelResource):
    class Meta:
        model = StepCount
