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
        try:    # TODO: @rahul this is a numb handler. at some point, you should remove this handler
            last_ten = Day.objects.all().order_by('-date')[:10]
            ordered = sorted(last_ten, key=operator.attrgetter('steps'))
            serialized_step_counts = []

            all_days = Day.objects.all().order_by('-date')
            index_of_today = len(all_days)

            with open('step-multipliers.csv', 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=',')
                # multipliers = list(csv_reader)

            multipliers = [['1', '1.25'], ['2', '1.94'], ['3', '1.09'], ['4', '1.15'], ['5', '1.24'], ['6', '1.35'], ['7', '1.35'], ['8', '1.42'], ['9', '1.67'], ['10', '1.88'], ['11', '1.80'], ['12', '1.80'], ['13', '1.80'], ['14', '1.80'], ['15', '1.80'], ['16', '1.80'], ['17', '1.80'], ['18', '1.80'], ['19', '1.80'], ['20', '1.80'], ['21', '1.80'], ['22', '1.80'], ['23', '1.80'], ['24', '1.80'], ['25', '1.60'], ['26', '1.50'], ['27', '1.40'], ['28', '1.30'], ['29', '1.90'], ['30', '1.90'], ['31', '1.90']]

            multiplier = multipliers[index_of_today][1]

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
                return Response('No new goal', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            from user_event_logs.models import EventLog
            EventLog.log(request.user, e, EventLog.ERROR)
            return Response(e.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
