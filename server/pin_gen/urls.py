from django.conf.urls import url

from .views import ClockFacePinView
from .views import pinArray
from .views import pinA, user

urlpatterns = [
    url(r'^arr/', pinArray, name="pin-gen-arr"),
    url(r'^pair/', ClockFacePinView.as_view(), name="pin-gen-pair"),
    url(r'^myarr/', pinA, name="pin-gen-myarr"),
    url(r'^user/', user, name="pin-gen-user")

]

