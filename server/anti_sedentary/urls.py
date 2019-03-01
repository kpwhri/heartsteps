from django.conf.urls import url
from .views import AntiSedentaryMessageCreateView

urlpatterns = [
    url(r'', AntiSedentaryMessageCreateView.as_view(), name='anti-sedentary-create')
]
