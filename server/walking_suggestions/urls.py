from django.conf.urls import url
from .views import WalkingSuggestionContextView

urlpatterns = [
    url(r'(?P<decision_id>[\w\-]+)', WalkingSuggestionContextView.as_view(), name='walking-suggestions-context')
]
