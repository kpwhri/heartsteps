from django.contrib import admin

from .models import FirstBoutPlanningTime
from .models import BoutPlanningNotification, Level, BoutPlanningDecision

class FirstBoutPlanningTimeAdmin(admin.ModelAdmin):
    list_display = ['user', 'hour', 'minute', 'active']
    fields = ['user', 'hour', 'minute', 'active']

admin.site.register(FirstBoutPlanningTime, FirstBoutPlanningTimeAdmin)


class BoutPlanningNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'level', 'when']
    fields = ['user', 'message', 'level', 'decision', 'when']

admin.site.register(BoutPlanningNotification, BoutPlanningNotificationAdmin)



class LevelAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'date']
    fields = ['user', 'level', 'date']

admin.site.register(Level, LevelAdmin)


class BoutPlanningDecisionAdmin(admin.ModelAdmin):
    list_display = ['user', 'N', 'O', 'R', 'return_bool', 'when_created']
    fields = ['user', 'N', 'O', 'R', 'return_bool', 'when_created', 'data']
    
admin.site.register(BoutPlanningDecision, BoutPlanningDecisionAdmin)