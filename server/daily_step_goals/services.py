import operator
import csv
from django.core.exceptions import ImproperlyConfigured

from .models import StepGoal, ActivityDay
from activity_summaries.models import Day

class StepGoalsService():

    class NotEnabled(ImproperlyConfigured):
        pass

    def __init__(self, user):
        assert user is not None, "User must be specified"
        
        self.user = user

    def create(self, date, message_framing=False):
        new_goal = StepGoal.objects.create(
            user = self.__user,
            date = date,
            step_goal = self.get_step_goal()
        )
        return new_goal

    def createMultiplierList():
        data = open("step-multipliers.csv")

        file = csv.dictReader(data)

        multipliers = []

        for col in file:
            multipliers.append(col['multiplier'])

        return multipliers

    def get_simple_step_goal(self, date=None):
        """returns step goal

        Args:
            date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

        Returns:
            [int]: step goal of the day
        """
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
            new_goal = (serialized_step_counts[4]["steps"] + serialized_step_counts[5]["steps"])/2;
            return new_goal
        else:
            return None

    def get_heartsteps_step_goal(self, date=None):
        """returns step goal

        Args:
            date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

        Returns:
            [int]: step goal of the day
        """
        last_ten = Day.objects.all().order_by('-date')[:10]
        ordered = sorted(last_ten, key=operator.attrgetter('steps'))
        serialized_step_counts = []

        all_days = Day.objects.all().order_by('-date')
        index_of_today = len(all_days)

        # multiplier =

        if ordered:
            for step in ordered:
                serialized_step_counts.append({
                    'date': step.date.strftime('%Y-%m-%d'),
                    'steps': step.steps
                })

            new_goal = (serialized_step_counts[4]["steps"] + serialized_step_counts[5]["steps"])/2;
            return new_goal
        else:
            return None
