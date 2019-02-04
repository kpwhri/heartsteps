from django.contrib import admin
from service_requests.models import ServiceRequest

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
