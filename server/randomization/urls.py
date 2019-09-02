from django.conf.urls import url

from .views import DecisionRatingView

urlpatterns = [
    url(r'(?P<decision_id>[\w\-]+)/rating', DecisionRatingView.as_view(), name='randomization-rating')
]
