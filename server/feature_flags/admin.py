from django.contrib import admin

from .models import FeatureFlags


class FeatureFlagsAdmin(admin.ModelAdmin):
    search_fields = ['user__username']


admin.site.register(FeatureFlags, FeatureFlagsAdmin)
