from django.contrib import admin

from .models import FirstBoutPlanningTime

class FirstBoutPlanningTimeAdmin(admin.ModelAdmin):
    list_display = ['user', 'hour', 'minute', 'active']
    fields = ['user', 'hour', 'minute', 'active']

admin.site.register(FirstBoutPlanningTime, FirstBoutPlanningTimeAdmin)
