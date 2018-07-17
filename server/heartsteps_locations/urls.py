from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'locations', views.LocationsView.as_view(), name='heartsteps-locations')
]
