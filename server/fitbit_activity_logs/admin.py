from django.contrib import admin

from activity_types.admin import ActivityTypeAdmin
from activity_types.models import ActivityType

from .models import FitbitActivityToActivityType

admin.site.unregister(ActivityType)

class ActivityTypeAdminExtended(ActivityTypeAdmin):
    readonly_fields = ['fitbit_activity_types']

    def fitbit_activity_types(self, activity_type):
        connections = FitbitActivityToActivityType.objects.filter(activity_type=activity_type).all()
        connections = list(connections)

        if len(connections) > 0:
            list_items = []
            for connection in connections:
                list_items.append('<p>%s (ID: %s)</p>' % (connection.fitbit_activity.name, connection.fitbit_activity.fitbit_id))
            return ''.join(list_items)
        else:
            return "No connected fitbit activity types"
    fitbit_activity_types.allow_tags = True

admin.site.register(ActivityType, ActivityTypeAdminExtended)
