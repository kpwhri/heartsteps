from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    url(r'tracker_register$', LoginView.as_view(template_name='register.html'),
        name='tracker-register'),
    url(r'logout$', LogoutView.as_view(), name='tracker-logout'),
]
