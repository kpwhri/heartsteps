from import_export import resources
from activity_logs.models import ActivityLog, ActivityLogSource
from anti_seds.models import StepCount

def underscore_to_camelcase(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)

# Whitelist the allowed tables for export
# table_whitelist = {
#     "activity_plan":        ActivityPlanResource,
#     "activity_log_source":  ActivityLogSource,
#     "activity_plan":        ActivityPlan,
#     "step_count":           StepCountResource
# }

# allowed_tables = {
#     "activity_logs":        "activity_log",
#     "activity_logs":        "activity_log_source",
#     "anti_seds":            "step_count"
# }

class StepCountResource(resources.ModelResource):
    class Meta:
        model = StepCount

# from django.app_labelps import apps
# from django.contrib.contenttypes.models import ContentType
# for model in apps.get_models():
#     content_type = ContentType.objects.get_for_model(model)
#     print(content_type.app_label)
#     print(content_type.model)
#     if content_type.app_label == "anti_seds":
#         importlib.import_module('models', content_type.app_label)
