from django.conf.urls import url
from .views import WalkingSuggestionCreateView

urlpatterns = [
    url(r'', WalkingSuggestionCreateView.as_view(), name='walking-suggestions-create')
]
