from django.conf.urls import url
from .views import CreateClockFace
from .views import ClockFaceStatus
from .views import ClockFacePair
from .views import ClockFaceStepCounts

urlpatterns = [
    url(r'create', CreateClockFace.as_view(), name='clock-face-create'),
    url(r'status', ClockFaceStatus.as_view(), name='clock-face-status'),
    url(r'pair', ClockFacePair.as_view(), name='clock-face-pair'),
    url(r'step-counts', ClockFaceStepCounts.as_view(), name='clock-face-step-counts')
]
