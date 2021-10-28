from django.contrib import admin

from .models import FitbitAccount, FitbitAccountUser, FitbitUpdate, FitbitSubscriptionUpdate, FitbitSubscription, FitbitAccountUpdate


class FitbitSubscriptionUpdateInline(admin.StackedInline):
    model = FitbitSubscriptionUpdate
    extra = 0


class FitbitAccountUserInline(admin.StackedInline):
    model = FitbitAccountUser
    extra = 0


class FitbitAccountAdmin(admin.ModelAdmin):
    inlines = [FitbitAccountUserInline]


admin.site.register(FitbitAccount, FitbitAccountAdmin)


class FitbitUpdateAdmin(admin.ModelAdmin):
    ordering = ["-created"]
    list_display = ['uuid', 'created', 'payload']
    inlines = [FitbitSubscriptionUpdateInline]


class FitbitSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'fitbit_account']
    readonly_fields = ['uuid', 'fitbit_account']


class FitbitAccountUpdateAdmin(admin.ModelAdmin):
    list_display = ['account', 'update', 'created']
    readonly_fields = ['account', 'update', 'created']


admin.site.register(FitbitUpdate, FitbitUpdateAdmin)
admin.site.register(FitbitSubscription, FitbitSubscriptionAdmin)
admin.site.register(FitbitAccountUpdate, FitbitAccountUpdateAdmin)