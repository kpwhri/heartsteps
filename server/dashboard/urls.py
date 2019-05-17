from django.conf.urls import url
from . import views

urlpatterns = [
    # url('', views.index, name='dashboard-index')
    url('', views.DashboardListView.as_view(), name='dashboard-index')
]
