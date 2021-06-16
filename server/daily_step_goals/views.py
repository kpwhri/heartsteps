from django.shortcuts import render

from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import StepGoals

def insertSteps():
    daily_step_goal_log = StepGoals()

    daily_step_goal_log.step_goal = getNewGoal()
    daily_step_goal_log.date = datetime.today()
    daily_step_goal_log.save()

def getNewGoal():
    last_ten = StepGoals.objects.all().order_by('-id')[:10]
    last_ten_in_ascending_order = reversed(last_ten)

    new_goal = last_ten_in_ascending_order[5]

    return new_goal

class DailyStepGoalsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):

        return Response({}, status=status.HTTP_400_BAD_REQUEST)
