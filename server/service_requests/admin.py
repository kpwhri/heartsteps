from math import floor
from django.contrib import admin

from import_export import resources
from import_export.admin import ExportMixin

from service_requests.models import ServiceRequest

class ServiceRequestResource(resources.ModelResource):

    class Meta:
        model = ServiceRequest
        fields = (
            'user__username',
            'url',
            'request_time',
            'request_data',
            'response_code',
            'response_time', 
            'response_data'    
        )
        export_order = [
            'user__username',
            'url',
            'request_time',
            'request_data',
            'response_code',
            'response_time',
            'response_data'
        ]

class ServiceRequestAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ServiceRequestResource
    date_hierarchy = 'request_time'

    list_display = ('name', 'sucessful', 'request_time', 'duration')
    readonly_fields = [
        'user',
        'url',
        'name',
        'duration',
        'request_data',
        'request_time',
        'response_code',
        'response_data',
        'response_time'
    ]

    search_fields = ['url', 'user__username', 'name']

    def sucessful(admin, instance):
        return instance.sucessful
    sucessful.boolean = True

    def duration(admin, instance):
        return '%d seconds' % instance.duration

admin.site.register(ServiceRequest, ServiceRequestAdmin)
