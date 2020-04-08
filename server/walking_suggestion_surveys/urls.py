from django.conf.urls import url
from .views import WalkingSuggestionSurveyTestView

urlpatterns = [
    url(r'test', WalkingSuggestionSurveyTestView.as_view(), name='walking-suggestion-survey-test')
]
