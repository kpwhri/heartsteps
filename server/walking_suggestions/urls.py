from django.conf.urls import url
from .views import WalkingSuggestionContextView, WalkingSuggestionCreateView

urlpatterns = [
    url(r'(?P<decision_id>[\w\-]+)', WalkingSuggestionContextView.as_view(), name='walking-suggestions-context'),
    url(r'', WalkingSuggestionCreateView.as_view(), name='walking-suggestions-create')
]
