from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^api/', include('participants.urls')),
    # url(r'', include('trackers.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'api-auth', include('rest_framework.urls'))
]
