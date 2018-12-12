from django.conf.urls import url
from .views import activity_types

urlpatterns = [
    url(r'types', activity_types, name='activity-types')
]
