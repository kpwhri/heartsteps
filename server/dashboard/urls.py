from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.login,
        {'template_name': 'dashboard/login.html'}, name='dashboard-login'),
    url('text', views.get_text_history, name='dashboard-text'),
    url('', views.DashboardListView.as_view(), name='dashboard-index'),
]
