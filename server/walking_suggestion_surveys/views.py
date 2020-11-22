from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import Configuration
from .models import WalkingSuggestionSurvey

class WalkingSuggestionSurveyTestView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            configuration = Configuration.objects.get(
                user = request.user,
                enabled = True
            )
            survey = configuration.create_survey()
            notification = survey.send_notification()
            return Response(
                {
                    'notificationId': str(notification.uuid)
                },
                status = status.HTTP_201_CREATED
            )
        except Configuration.DoesNotExist:
            return Response('Not configured', status.HTTP_400_BAD_REQUEST)
        except WalkingSuggestionSurvey.NotificationSendError:
            return Response('Unable to send notification', status.HTTP_400_BAD_REQUEST)
