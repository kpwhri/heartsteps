from django.apps import apps
from import_export import resources
from activity_logs.models import ActivityLog, ActivityLogSource
from anti_seds.models import StepCount

MODEL_NOT_FOUND = "Model not found. Export unavailable."

def underscore_to_camelcase(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)[:-1]

def get_model_from_table_name(table_name):
    model_name = underscore_to_camelcase(table_name)
    try:
        return apps.get_model(table_name, model_name=model_name)
    except LookupError:
        return MODEL_NOT_FOUND

# Create an instance of ModelResource linked to appropriate Model
def create_resource(table_name, baseclass=resources.ModelResource):
    current_model = get_model_from_table_name(table_name)
    if current_model == MODEL_NOT_FOUND:
        return MODEL_NOT_FOUND
    else:
        resource = current_model.__name__ + "Resource"
        class Meta:
            model = current_model
        attrs = {'__module__': baseclass.__module__, 'Meta': Meta}
        newclass = type(str(resource), (baseclass,), attrs)
        globals()[resource] = newclass
        return globals()[resource]
