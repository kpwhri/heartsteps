from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'login', views.LoginView.as_view(), name='participants-login'),
    url(r'enroll', views.EnrollView.as_view(), name='participants-enroll'),
    url(r'information', views.ParticipantInformationView.as_view(), name='participants-information')
]
