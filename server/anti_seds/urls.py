from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'stepdata', views.StepCountUpdateView.as_view(), name='anti-sed-steps')
]
