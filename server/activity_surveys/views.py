from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .services import ActivitySurveyService

class ActivitySurveyTestView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            service = ActivitySurveyService(user = request.user)
            activity_survey = service.create_test_survey()
            notification = service.send_notification(activity_survey)
            return Response(
                {
                    'notificationId': notification.uuid
                },
                status = status.HTTP_201_CREATED
            )
        except ActivitySurveyService.NotConfigured:
            return Response('Not configured', status.HTTP_400_BAD_REQUEST)
        except ActivitySurveyService.NotificationSendError:
            return Response('Unable to send notification', status.HTTP_400_BAD_REQUEST)
