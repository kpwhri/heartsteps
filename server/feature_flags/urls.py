from django.conf.urls import url
from .views import FeatureFlagsList

urlpatterns = [
    url(r'feature-flags', FeatureFlagsList.as_view(), name='feature-flags-list')
]
