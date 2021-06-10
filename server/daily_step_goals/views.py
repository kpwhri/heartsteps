from django.shortcuts import render

from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .serializers import ActivityLogSerializer, TimeRangeSerializer
from .models import StepGoals

def insertSteps():
    daily_step_goal_log = StepGoals()

    daily_step_goal_log.step_goal = 8000
    daily_step_goal_log.date = datetime.today()
    daily_step_goal_log.save()

