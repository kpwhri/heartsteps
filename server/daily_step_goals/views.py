from django.shortcuts import render

from datetime import datetime
import operator
import csv

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import StepGoal, ActivityDay
from activity_summaries.models import Day

from django.contrib.staticfiles import finders

def insertSteps():
    daily_step_goal_log = StepGoal()

    # daily_step_goal_log.step_goal = getNewGoal()
    daily_step_goal_log.date = datetime.today()
    daily_step_goal_log.save()

class DailyStepGoalsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        step_goals = StepGoal.objects.filter(
            user = request.user
        ).order_by('date') \
        .all()

        if step_goals:
            serialized_step_goals = []
            for step_goal in step_goals:
                serialized_step_goals.append({
                    'date': step_goal.date.strftime('%Y-%m-%d'),
                    'step_goal': step_goal.step_goal
                })
            return Response(serialized_step_goals)
        else:
            return Response('No step goals', status=status.HTTP_404_NOT_FOUND)

class NewGoal(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        last_ten = Day.objects.all().order_by('-date')[:10]
        ordered = sorted(last_ten, key=operator.attrgetter('steps'))
        serialized_step_counts = []

        if ordered:
            for step in ordered:
                serialized_step_counts.append({
                    'date': step.date.strftime('%Y-%m-%d'),
                    'steps': step.steps
                })
        # last_ten_in_ascending_order = reversed(last_ten)
        # new_goal = last_ten_in_ascending_order[5].steps
            return Response(serialized_step_counts)
        else:
            return Response('No new goal', status=status.HTTP_404_NOT_FOUND)

class NewGoalCalc(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        last_ten = Day.objects.all().order_by('-date')[:10]
        ordered = sorted(last_ten, key=operator.attrgetter('steps'))
        serialized_step_counts = []

        all_days = Day.objects.all().order_by('-date')
        index_of_today = len(all_days)

        # csv_path = finders.find('data/step-multipliers.csv')
        # csv_reader = csv.reader(csv_path, delimiter=',')

        with open('step-multipliers.csv', 'r', newline='') as csv_file:
            fieldnames = ['day', 'multiplier']
            csv_reader = csv.DictReader(csv_file, delimiter=',', fieldnames='fieldnames')
            multipliers = list(csv_reader)
            # multiplier = multipliers[index_of_today]

        multiplier = 5

        if ordered:
            for step in ordered:
                serialized_step_counts.append({
                    'date': step.date.strftime('%Y-%m-%d'),
                    'steps': step.steps,
                    'multiplier': multiplier
                })

            # new_goal = (serialized_step_counts[4]["steps"] + serialized_step_counts[5]["steps"])/2
            # new_goal *= multiplier
            # serialized_step_goal = []
            # serialized_step_goal.append({
            #         'goal': new_goal
            #     })
            return Response(serialized_step_counts)
        else:
            return Response('No new goal', status=status.HTTP_404_NOT_FOUND)
