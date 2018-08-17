from django.conf.urls import url
from .views import DecisionView

urlpatterns = [
    url(r'decisions', DecisionView.as_view(), name='randomization-decision-create')
]
