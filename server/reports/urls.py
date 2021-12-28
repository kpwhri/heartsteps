from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'download', DownloadReportView.as_view(), name='some_view_download')
]
