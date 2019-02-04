from django.apps import apps
from django.db import connection
from import_export import resources

MODEL_NOT_FOUND = "Model not found. Export unavailable."
MULTIPLE_MODELS_FOUND = "More than one model has that name. Models defined more than once cannot be exported."
MODEL_LOOKUP_ERROR = "Unknown error raised in model lookup."
EXCEPTION_FOUND = [MODEL_NOT_FOUND, MULTIPLE_MODELS_FOUND, MODEL_LOOKUP_ERROR]

def underscore_to_camelcase(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)[:-1]

def get_model_from_model_list(table_list):
    if len(table_list) == 1:
        return(table_list[0])
    elif len(table_list) == 0:
        return MODEL_NOT_FOUND
    elif len(table_list) > 1:
        return MULTIPLE_MODELS_FOUND
    else:
        return MODEL_LOOKUP_ERROR

def get_model_from_table_name(table_name):
    model_name = underscore_to_camelcase(table_name)
    tables = connection.introspection.table_names()
    available_models = connection.introspection.installed_models(tables)
    table_list = [table for table in available_models if table.__name__ == model_name]
    return get_model_from_model_list(table_list)

# Create an instance of ModelResource linked to appropriate Model
def create_resource(table_name, baseclass=resources.ModelResource):
    current_model = get_model_from_table_name(table_name)
    if current_model in EXCEPTION_FOUND:
        return current_model
    else:
        resource = current_model.__name__ + "Resource"
        class Meta:
            model = current_model
        attrs = {'__module__': baseclass.__module__, 'Meta': Meta}
        newclass = type(str(resource), (baseclass,), attrs)
        globals()[resource] = newclass
        return globals()[resource]
