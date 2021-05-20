from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .services import BoutPlanningService

class BoutPlanningMessageCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        bout_planning_service = BoutPlanningService.create_service(
            username = request.user.username
        )
        message = bout_planning_service.send_message("test intervention", "Notification.BoutPlanning", "Sample Title", "Sample Body", False)
        return Response(
            {
                'messageId': str(message.data["messageId"])
            },
            status = status.HTTP_201_CREATED
        )

