from django.conf.urls import url
from .views import DailyWeatherView
from .views import DailyWeatherRangeView
from .views import DailyWeatherUpdateForecastsView

urlpatterns = [
    url(r'weather/update', DailyWeatherUpdateForecastsView.as_view(), name='weather-update'),
    url(r'weather/(?P<start>[\w\-]+)/(?P<end>[\w\-]+)', DailyWeatherRangeView.as_view(), name='weather-range'),
    url(r'weather/(?P<day>[\w\-]+)', DailyWeatherView.as_view(), name='weather-day')
]
