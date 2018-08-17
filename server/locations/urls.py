from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'places', views.PlacesView.as_view(), name='locations-places')
]
