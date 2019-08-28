from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .services import AntiSedentaryDecisionService

class AntiSedentaryMessageCreateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        decision_service = AntiSedentaryDecisionService.create_decision(
            user = request.user,
            test = True
        )
        decision_service.decide()
        decision_service.update_context()
        decision_service.send_message()

        decision = decision_service.decision
        return Response(
            {
                'id': str(decision.id),
                'messageId': str(decision.notification.uuid)
            },
            status = status.HTTP_201_CREATED
        )

