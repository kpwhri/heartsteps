from django.conf.urls import url
from .views import SuggestionTimeList

urlpatterns = [
    url(r'times', SuggestionTimeList.as_view(), name='activity_suggestions-times')
]
