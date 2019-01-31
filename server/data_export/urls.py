from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'step_count/', views.export_step_count)
    #(url(r'(?P<export_table>[a-zA-Z_]+$)', views.export_table))
]
