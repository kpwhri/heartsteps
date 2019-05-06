from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'reflection-time', views.ReflectionTimeView.as_view(), name='weekly-reflection-time')
]
