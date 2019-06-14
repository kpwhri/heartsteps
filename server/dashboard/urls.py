from django.conf.urls import url
from . import views

urlpatterns = [
    url('', views.DashboardListView.as_view(), name='dashboard-index')
]
