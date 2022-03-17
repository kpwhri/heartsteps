from django.contrib import admin

from system_settings.models import StudySetting
from system_settings.models import SystemSetting

class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    fields = ['key', 'value']

admin.site.register(SystemSetting, SystemSettingAdmin)

class StudySettingAdmin(admin.ModelAdmin):
    list_display = ['study', 'key', 'value']
    fields = ['study', 'key', 'value']

admin.site.register(StudySetting, StudySettingAdmin)
