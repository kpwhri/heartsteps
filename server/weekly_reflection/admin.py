from django.contrib import admin

from .models import ReflectionTime

class WeeklyReflectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'formatted_time', 'active']
    fields = ['user', 'day', 'time', 'active', 'next_run']
    readonly_fields = ['user', 'next_run']

    def next_run(self, reflection_time):
        next_run = reflection_time.get_next_time()
        return next_run.strftime('%Y-%m-%d %H:%M')

admin.site.register(ReflectionTime, WeeklyReflectionAdmin)
