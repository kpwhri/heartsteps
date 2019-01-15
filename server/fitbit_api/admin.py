from django.contrib import admin
from .models import FitbitAccount, FitbitAccountUser, FitbitDay, FitbitActivity, FitbitUpdate, FitbitSubscriptionUpdate

class FitbitSubscriptionUpdateInline(admin.StackedInline):
    model = FitbitSubscriptionUpdate
    extra = 0

class FitbitActivityInline(admin.StackedInline):
    model = FitbitActivity
    extra = 0

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

class FitbitDayAdmin(admin.ModelAdmin):
    ordering = ["-date"]
    list_display = ("__str__", "last_updated")
    
    inlines = [
        FitbitActivityInline
    ]

    def last_updated(self, fitbit_day):
        return fitbit_day.updated.strftime("%Y-%m-%d %H:%M")

admin.site.register(FitbitDay, FitbitDayAdmin)
