from django.conf.urls import url

from .views import ClockFacePinView
from .views import pinArray

urlpatterns = [
    url(r'^arr/', pinArray),
    url(r'pair/', ClockFacePinView.as_view(), name="pin-gen-pair")
]

