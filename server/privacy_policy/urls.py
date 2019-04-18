from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'privacy-policy', TemplateView.as_view(template_name='privacy_policy/privacy_policy.html'))
]
