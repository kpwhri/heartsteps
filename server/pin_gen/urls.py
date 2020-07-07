from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get/', views.index),
    url(r'^arr/', views.pinArray)
]

