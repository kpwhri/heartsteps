from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'login', views.LoginView.as_view(), name='watch-app-login'),
    url(r'steps', views.StepCountUpdateView.as_view(), name='watch-app-steps'),
    url(r'status', views.WatchAppStatusView.as_view(), name='watch-app-status')
]
