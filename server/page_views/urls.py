from django.conf.urls import url
from .views import PageViewView

urlpatterns = [
    url(r'page-views', PageViewView.as_view(), name='page-views')
]
