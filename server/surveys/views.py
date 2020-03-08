from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import Survey

class SurveyResponseView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, survey_id):
        try:
            survey = Survey.objects.get(
                uuid=survey_id,
                user = request.user
            )
        except Survey.DoesNotExist:
            return Response(
                'Survey does not exist',
                status = status.HTTP_400_BAD_REQUEST
            )
        for key in request.data:
            survey.save_response(key, request.data[key])
        return Response(request.data, status.HTTP_200_OK)

