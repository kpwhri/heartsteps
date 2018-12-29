from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from .models import WeeklyGoal, Week

class GoalsListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response('', status=status.HTTP_400_BAD_REQUEST)

class GoalView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_week(self, week_id, user):
        try:
            return Week.objects.get(
                uuid = week_id,
                user = user
            )
        except Week.DoesNotExist:
            raise Http404()

    def get(self, request, week_id):
        week = self.get_week(week_id, request.user)
        try:
            weekly_goal = WeeklyGoal.objects.get(
                user = request.user,
                week = week
            )
        except WeeklyGoal.DoesNotExist:
            weekly_goal = WeeklyGoal.objects.create(
                user = request.user,
                week = week,
                minutes = 95,
                confidence = 0.5
            )
        return Response({
            'minutes': weekly_goal.minutes,
            'confidence': weekly_goal.confidence
        }, status = status.HTTP_200_OK)

    def post(self, request, week_id):
        week = self.get_week(week_id, request.user)
        weekly_goal, _ = WeeklyGoal.objects.update_or_create(
            user = request.user,
            week = week,
            defaults = {
                'minutes': request.data['minutes'],
                'confidence': request.data['confidence']
            }
        )
        return Response({
            'minutes': weekly_goal.minutes,
            'confidence': weekly_goal.confidence
        }, status=status.HTTP_200_OK)
