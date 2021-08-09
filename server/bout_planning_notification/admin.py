from django.contrib import admin

from .models import FirstBoutPlanningTime

class FirstBoutPlanningTimeAdmin(admin.ModelAdmin):
    list_display = ['user', 'time', 'active']
    fields = ['user', 'time', 'active']

admin.site.register(FirstBoutPlanningTime, FirstBoutPlanningTimeAdmin)
