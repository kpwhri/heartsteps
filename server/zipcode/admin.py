from django.contrib import admin

from zipcode.models import ZipCodeRequestHistory

# Register your models here.

class ZipCodeRequestHistoryAdmin(admin.ModelAdmin):
    list_display = ['zipcode', 'user', 'when_requested']
    readonly_fields = ['zipcode', 'user', 'when_requested', 'response_code', 'response_message', 'latitude', 'longitude', 'state', 'city']

admin.site.register(ZipCodeRequestHistory, ZipCodeRequestHistoryAdmin)