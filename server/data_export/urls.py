from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'(?P<export_table>[a-zA-Z_]+$)', views.export_table, name='data-export')
]
