from django.contrib import admin
from .models import AuditEntry, EventLog

@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ['action', 'username', 'ip',]
    list_filter = ['action',]

admin.site.register(EventLog)
