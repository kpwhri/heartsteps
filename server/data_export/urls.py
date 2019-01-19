from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'steps', views.export_step_count, name='export-steps')
]
