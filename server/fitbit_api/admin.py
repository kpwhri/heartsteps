from django.contrib import admin
from django.contrib import messages

from .models import FitbitAccount, FitbitAccountUser, FitbitDay, FitbitActivity, FitbitUpdate, FitbitSubscriptionUpdate
from .services import FitbitDayService

class FitbitSubscriptionUpdateInline(admin.StackedInline):
    model = FitbitSubscriptionUpdate
    extra = 0

class FitbitActivityInline(admin.StackedInline):
    model = FitbitActivity
    extra = 0
    fields = ['type', 'duration', 'average_heart_rate']
    readonly_fields = ['type', 'duration', 'average_heart_rate']

    def duration(self, instance):
        return '%s minutes' % instance.duration

class FitbitAccountUserInline(admin.StackedInline):
    model = FitbitAccountUser
    extra = 0

class FitbitAccountAdmin(admin.ModelAdmin):
    inlines = [
        FitbitAccountUserInline
    ]
admin.site.register(FitbitAccount, FitbitAccountAdmin)

class FitbitUpdateAdmin(admin.ModelAdmin):
    ordering = ["-created"]

    inlines = [
        FitbitSubscriptionUpdateInline
    ]

admin.site.register(FitbitUpdate, FitbitUpdateAdmin)

def update_fitbit_day(modeladmin, request, queryset):
    for day in queryset:
        service = FitbitDayService(fitbit_day = day)
        service.update()
        messages.add_message(request, messages.INFO, 'Updated %s' % (day))


class FitbitDayAdmin(admin.ModelAdmin):
    ordering = ["-date"]
    list_display = ("__str__", "last_updated")

    exclude = ['uuid']
    readonly_fields = ['account', 'date', 'timezone','step_count']
    actions = [update_fitbit_day]
    
    inlines = [
        FitbitActivityInline
    ]

    def last_updated(self, fitbit_day):
        return fitbit_day.updated.strftime("%Y-%m-%d %H:%M")

admin.site.register(FitbitDay, FitbitDayAdmin)
