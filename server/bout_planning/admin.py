from datetime import timedelta

from django.contrib import admin

from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field

from behavioral_messages.admin import MessageTemplateAdmin
from randomization.admin import DecisionAdmin
from randomization.resources import DecisionResource
from service_requests.admin import ServiceRequestAdmin

from .models import GenericMessagesConfiguration
from .services import BoutPlanningService


class GenericMessagesAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['user', 'enabled']
    actions = [
        ]
    readonly_fields = [
    ]

admin.site.register(GenericMessagesConfiguration, GenericMessagesAdmin)