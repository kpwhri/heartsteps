from django.contrib import admin

from .models import FirstBoutPlanningTime

class FirstBoutPlanningTimeAdmin(admin.ModelAdmin):
    list_display = ['user', 'formatted_time', 'active']
    fields = ['user', 'time', 'active']

admin.site.register(FirstBoutPlanningTime, FirstBoutPlanningTimeAdmin)
