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
    list_display = ['study', 'account_sid']
    fields = ['study', 'account_sid', 'auth_token']

admin.site.register(TwilioAccountInfo, TwilioAccountInfoAdmin)