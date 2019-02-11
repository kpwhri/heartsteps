from django.conf.urls import url
from .views import ActivityTypesList

urlpatterns = [
    url(r'types', ActivityTypesList.as_view(), name='activity-types')
]
