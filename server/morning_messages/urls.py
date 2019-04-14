from django.conf.urls import url

from .views import AnchorMessageView, MorningMessageView, MorningMessageSurveyView

urlpatterns = [
    url(r'morning-messages/(?P<day>[\w\-]+)/survey', MorningMessageSurveyView.as_view(), name='morning-messages-survey'),
    url(r'morning-messages/(?P<day>[\w\-]+)', MorningMessageView.as_view(), name='morning-messages-day'),
    url(r'anchor-message/(?P<day>[\w\-]+)', AnchorMessageView.as_view(), name="anchor-message-view")
]
