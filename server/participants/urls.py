from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'enroll', views.enroll, name='participants-enroll')
]
