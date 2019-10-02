from django.conf.urls import url
from .views import (LoginView, LogoutView, EnrollView,
                    ParticipantInformationView, ParticipantAddView)

urlpatterns = [
    url(r'login', LoginView.as_view(), name='participants-login'),
    url(r'logout', LogoutView.as_view(), name='participants-logout'),
    url(r'enroll', EnrollView.as_view(), name='participants-enroll'),
    url(r'information', ParticipantInformationView.as_view(),
        name='participants-information'),
    url(r'participant-add', ParticipantAddView.as_view(),
        name='participant-add')
]
