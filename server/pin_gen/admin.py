from django.contrib import admin
from .models import *

# Register your models here.
class pinAdmin(admin.ModelAdmin):
	pass

admin.site.register(Pin, pinAdmin)


