from django.conf.urls import url
from locations.views import PlacesView, LocationUpdateView

urlpatterns = [
    url(r'places', PlacesView.as_view(), name='locations-places'),
    url(r'locations', LocationUpdateView.as_view(), name='locations-update')
]
