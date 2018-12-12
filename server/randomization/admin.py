from django.contrib import admin

class DecisionAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'
    search_fields = [
        'user__username'
    ]
