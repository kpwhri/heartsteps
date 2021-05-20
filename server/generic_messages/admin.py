from datetime import timedelta

from django.contrib import admin

from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field

from .models import GenericMessagesConfiguration

class GenericMessagesAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['user', 'enabled']
    actions = [
        ]
    readonly_fields = [
    ]

admin.site.register(GenericMessagesConfiguration, GenericMessagesAdmin)