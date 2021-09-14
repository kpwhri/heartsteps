import operator
import csv
from django.core.exceptions import ImproperlyConfigured

from .models import StepGoal, ActivityDay
from activity_summaries.models import Day

from .models import User, StepGoalPRBScsv
from user_event_logs.models import EventLog
from days.services import DayService
from participants.models import Participant


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
            cohort = query.get().cohort
            
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
            
        steps_list = Day.objects.filter(user=self.user, date__lte=date).order_by('-date').all()[:(self.number_of_previous_days)]
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
        median = self.get_median_steps(date=date)
        EventLog.log(self.user, "Step goal could fetched and calculated correctly.", EventLog.INFO)
        
        # TODO: This should be changed to the actual implementation
        return median

        

    def get_heartsteps_step_goal(self, date=None):
        """returns step goal

        Args:
            date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

        Returns:
            [int]: step goal of the day
        """

        user = User.objects.get(self.__user.username)

        last_ten = Day.objects.all().order_by('-date')[:10]
        ordered = sorted(last_ten, key=operator.attrgetter('steps'))
        serialized_step_counts = []

        all_days = Day.objects.all().order_by('-date')
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
