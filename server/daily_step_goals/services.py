import operator
import csv
from django.core.exceptions import ImproperlyConfigured

from .models import StepGoal
# from activity_summaries.models import Day as ActivitySummaryDay
import activity_summaries.models

from .models import User, StepGoalPRBScsv
from user_event_logs.models import EventLog
from days.services import DayService
from participants.models import Participant

from datetime import timedelta

class StepGoalsService():
    number_of_previous_days = 10
    magnitude = 2000    # 2000 steps x PRBS
    
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

    def generate_dump_goal_sequence(self, date=None):
        query = Participant.objects.filter(user=self.user)
        if query.exists():
            cohort = query.first().cohort
            
            PRBS_list = StepGoalPRBScsv.get_seq(cohort)
            
            base = self.get_median_steps(date=date)
            
            goal_sequence = [int(base + (self.magnitude * x)) for x in PRBS_list]
            
            return goal_sequence
        else:
            raise RuntimeError("No matching Participant for {}".format(self.user))
    
    def get_median_steps(self, date=None):
        if date is None:
            day_service = DayService(self.user)
            date = day_service.get_current_date()
            
        steps_list = activity_summaries.models.Day.objects.filter(user=self.user, date__lte=date).order_by('-date').all()[:(self.number_of_previous_days)]
        ordered = sorted(steps_list, key=operator.attrgetter('steps'))
        
        len_steps_list = len(steps_list)
        if len_steps_list > 0:
            if len_steps_list % 2 == 0:
                half = int(len_steps_list / 2)
                median = int((ordered[half].steps + ordered[half+1].steps)/2)
            else:
                half = int((len_steps_list - 1)/ 2)
                median = ordered[half].steps
            return median
        else:
            raise RuntimeError("No Step Data")
    
    def get_step_goal(self, date=None):
        """returns step goal

        Args:
            date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

        Returns:
            [int]: step goal of the day
        """
        
        
        try:
            goal = StepGoal.get(user=self.user, date=date)
            EventLog.info(self.user, "Returning goal: {}".format(goal))
            return goal
        except ValueError:
            median = self.get_median_steps(date=date)
            EventLog.info(self.user, "Step goal is not found. Calculating... date={}".format(date))
            prbs_list = self.generate_dump_goal_sequence(date=date)
            if date is None:
                day_service = DayService(user = self.user)
                date = day_service.get_current_date()
                
            for i in range(0, len(prbs_list)):
                StepGoal.objects.create(user=self.user, step_goal=prbs_list[i], date=(date + (timedelta(days=1) * i)))
            
            step_goal = StepGoal.objects.filter(user=self.user, date=date).first().step_goal
            EventLog.log(self.user, "Step goal could fetched and calculated correctly: {}".format(step_goal), EventLog.INFO)
            return step_goal

    def get_heartsteps_step_goal(self, date=None):
        """returns step goal

        Args:
            date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

        Returns:
            [int]: step goal of the day
        """

        user = User.objects.get(self.__user.username)

        last_ten = activity_summaries.models.Day.objects.all().order_by('-date')[:10]
        ordered = sorted(last_ten, key=operator.attrgetter('steps'))
        serialized_step_counts = []

        all_days = activity_summaries.models.Day.objects.all().order_by('-date')
        index_of_today = len(all_days)

        with open('step-multipliers.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            multipliers = list(csv_reader)

        multiplier = multipliers[index_of_today][1]

        if ordered:
            for step in ordered:
                serialized_step_counts.append({
                    'date': step.date.strftime('%Y-%m-%d'),
                    'steps': step.steps
                })

            new_goal = (serialized_step_counts[4]["steps"] + serialized_step_counts[5]["steps"])/2
            new_goal *= multiplier

            EventLog.log(user, "Step goal could fetched and calculated correctly.", EventLog.INFO)

            return new_goal
        else:
            EventLog.log(user, "Step goal could not be fetched. Ordered list could not be defined.", EventLog.ERROR)
            return None
