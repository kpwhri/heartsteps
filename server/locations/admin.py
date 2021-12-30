from django.contrib import admin

from .models import Place, Location

class PlaceAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'latitude', 'longitude', 'type']
    fields = ['user', 'address', 'latitude', 'longitude', 'type']

class LocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'latitude', 'longitude', 'time', 'source', 'category']
    fields = ['user', 'latitude', 'longitude', 'time', 'source', 'category']


admin.site.register(Place, PlaceAdmin)
admin.site.register(Location, LocationAdmin)