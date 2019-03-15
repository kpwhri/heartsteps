from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'contact-information', views.ContactInformationView.as_view(), name='contact-information')
]
