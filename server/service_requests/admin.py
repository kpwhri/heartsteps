from math import floor
from django.contrib import admin
from service_requests.models import ServiceRequest

class ServiceRequestAdmin(admin.ModelAdmin):
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
