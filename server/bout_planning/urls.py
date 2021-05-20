from django.conf.urls import url
from .views import BoutPlanningMessageCreateView

urlpatterns = [
    url(r'', BoutPlanningMessageCreateView.as_view(), name='bout-planning-create')
]
