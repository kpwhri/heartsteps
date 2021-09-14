from django.contrib import admin
from django.contrib import messages

from fitbit_api.services import FitbitClient

from .models import FitbitDay, FitbitActivity, FitbitMinuteStepCount
from .services import FitbitDayService

def update_fitbit_day(modeladmin, request, queryset):
    for day in queryset:
        try:
            service = FitbitDayService(fitbit_day = day)
            service.update()
            messages.add_message(request, messages.INFO, 'Updated %s' % day)
        except FitbitClient.ClientError:
            messages.add_message(request, messages.ERROR, 'Failed to update %s' % day)


class FitbitDayAdmin(admin.ModelAdmin):
    ordering = ["-date"]
    list_display = ("__str__", "last_updated")

    exclude = ['uuid']
    readonly_fields = ['account', 'date', 'timezone','step_count', 'activities']
    actions = [update_fitbit_day]

    def activities(self, fitbit_day):
        activities = []
        for activity in fitbit_day.activities:
            activities.append("{id}: {type} at {time} ({duration} minutes)".format(
                id = activity.fitbit_id,
                type = activity.type.name,
                time = activity.start_time.astimezone(fitbit_day.timezone).strftime("%H:%M"),
                duration = activity.duration
            ))
        return '<ul><li>' + '</li><li>'.join(activities) + '</li></ul>'
    activities.allow_tags=True

    def last_updated(self, fitbit_day):
        return fitbit_day.updated.strftime("%Y-%m-%d %H:%M")

admin.site.register(FitbitDay, FitbitDayAdmin)



class FitbitMinuteStepCountAdmin(admin.ModelAdmin):
    ordering = ["account", "-time"]
    list_display = ("account", "time", "steps")

    readonly_fields = ['account', 'time', 'steps']

admin.site.register(FitbitMinuteStepCount, FitbitMinuteStepCountAdmin)