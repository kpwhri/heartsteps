from django.conf.urls import url
from .views import DecisionView, DecisionUpdateView

urlpatterns = [
    url(r'decisions/(?P<decision_id>[0-9a-f-]+)', DecisionUpdateView.as_view(), name="heartsteps-decisions-update"),
    url(r'decisions', DecisionView.as_view(), name='heartsteps-decisions-create')
]
