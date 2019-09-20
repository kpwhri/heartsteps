from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import CohortListView
from .views import DashboardListView
from .views import get_text_history

urlpatterns = [
    url(
        r'^login/$',
        auth_views.login,
        {
            'template_name': 'dashboard/login.html'
        },
        name='dashboard-login'
    ),
    url('text', get_text_history, name='dashboard-text'),
    url('(?P<cohort_id>[\d]+)', DashboardListView.as_view(), name='dashboard-cohort-participants'),
    url('', CohortListView.as_view(), name='dashboard-cohorts')
]
