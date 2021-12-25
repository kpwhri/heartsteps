from django.contrib import admin

from .models import Contact, TwilioAccountInfo
from .models import Message

class ContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'number', 'enabled']

admin.site.register(Contact, ContactAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'recipient', 'sender', 'body', 'created']

    readonly_fields = [
        'recipient',
        'sender',
        'body',
        'created'
        ]

admin.site.register(Message, MessageAdmin)


class TwilioAccountInfoAdmin(admin.ModelAdmin):
    list_display = ['study', 'account_sid', 'from_phone_number']
    fields = ['study', 'account_sid', 'auth_token', 'from_phone_number']

admin.site.register(TwilioAccountInfo, TwilioAccountInfoAdmin)