from django.conf.urls import url

from .views import SurveyResponseView

urlpatterns = [
    url(r'(?P<survey_id>[\w\-]+)/response', SurveyResponseView.as_view(), name='survey-response')
]
