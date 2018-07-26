from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'forecasts/(?P<pk>[0-9]+)/$', views.WeatherForecastsDetail.as_view(), name='weather-detail'),
    url(r'forecasts/$', views.WeatherForecastsList.as_view(), name='weather-list')
]

urlpatterns = format_suffix_patterns(urlpatterns)