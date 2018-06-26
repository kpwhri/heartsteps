from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'enroll', views.EnrollView.as_view(), name='participants-enroll'),
    url(r'firebaseToken', views.FirebaseTokenView.as_view(), name='participants-firebase-token')
]
