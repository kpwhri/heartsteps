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

        list_items = []
        if len(connections) > 0:            
            for connection in connections:
                if connection:
                    list_items.append('%s (ID: %s)' % (connection.fitbit_activity_type.name, connection.fitbit_activity_type.fitbit_id))
        if len(list_items) > 0:
            return ''.join(list_items)
        else:
            return "No connected fitbit activity types"
    fitbit_activity_types.allow_tags = True

admin.site.register(ActivityType, ActivityTypeAdminExtended)
