from django.conf.urls import url

from .views import ClockFacePinView
from .views import pinArray
from . import views

urlpatterns = [
    url(r'^arr/', pinArray),
    url(r'^pair/', ClockFacePinView.as_view(), name="pin-gen-pair"),
    url(r'^myarr/', views.pinA),
    url(r'^user/', views.user)

]

