from django.contrib import admin

from .models import SendSMS

class SMSAdmin(admin.ModelAdmin):
    list_display = [
        'to_number',
        'body',
        'sent_at'
    ]
    
admin.site.register(SendSMS, SMSAdmin)
