from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Week
from .serializers import GoalSerializer, WeekSerializer, SurveySerializer
from .services import WeekService

class WeekView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_week(self, user, week_number=None):
        if not week_number:
            return self.get_current_week(user)
        try:
            return Week.objects.get(
                number = week_number,
                user = user
            )
        except Week.DoesNotExist:
            raise Http404()

    def get_current_week(self, user):
        service = WeekService(user)
        try:
            return service.get_current_week()
        except WeekService.WeekDoesNotExist:
            service.update_weeks()
            return service.get_current_week()

    def get(self, request, week_number=None):
        week = self.get_week(request.user, week_number)
        serialized = WeekSerializer(week)
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def post(self, request, week_number=None):
        week = self.get_week(request.user, week_number)
        serialized = GoalSerializer(data=request.data)
        if serialized.is_valid():
            week.goal = serialized.validated_data['goal']
            week.confidence = serialized.validated_data['confidence']
            week.save()

            serialized_week = WeekSerializer(week)
            return Response(serialized_week.data, status=status.HTTP_200_OK)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

class NextWeekView(WeekView):

    def get_week(self, user, week_number=None):
        service = WeekService(user)
        return service.get_next_week()

class SendReflectionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        service = WeekService(request.user)
        week = service.get_current_week()
        service.send_reflection(week)

        return Response({}, status=status.HTTP_201_CREATED)

class WeekSurveyView(WeekView):

    def get_week_survey(self, request, week_number):
        week = self.get_week(request.user, week_number)
        if not week.survey:
            raise Http404()
        else:
            return week.survey

    def get(self, request, week_number):
        survey = self.get_week_survey(request, week_number)
        serialized = SurveySerializer(survey)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, week_number):
        survey = self.get_week_survey(request, week_number)

        for key in request.data:
            survey.save_response(key, request.data[key])

        serialized = SurveySerializer(survey)
        return Response(serialized.data, status=status.HTTP_200_OK)