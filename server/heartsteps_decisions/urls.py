from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'decisions', views.DecisionView.as_view(), name='heartsteps-decisions')
]
