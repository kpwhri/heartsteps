from django.conf.urls import url
from .views import SuggestionTimeList

urlpatterns = [
    url(r'', SuggestionTimeList.as_view(), name='walking-suggestion-times')
]
