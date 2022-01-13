import datetime
import operator
import csv
from django.core.exceptions import ImproperlyConfigured
from statistics import median

from daily_step_goals.tasks import update_goal
from .models import StepGoal, StepGoalCalculationSettings, StepGoalSequence, StepGoalSequence_User, StepGoalSequenceBlock, StepGoalsEvidence
# from activity_summaries.models import Day as ActivitySummaryDay
import activity_summaries.models

from .models import User
from user_event_logs.models import EventLog
from days.services import DayService
from participants.models import Participant

from datetime import timedelta

class StepGoalsService:
    # number_of_previous_days = 10
    # magnitude = 2000    # 2000 steps x PRBS
    
    class NotEnabled(ImproperlyConfigured):
        pass

    def __init__(self, user):
        assert user is not None, "User must be specified"
        
        self.user = user
        self.participant = Participant.objects.get(user=self.user)
        self.cohort = self.participant.cohort

    def get_seq(self):
        cohort = self.cohort
        
        default_seq = [0.3,0.4,0.5,0.6,0.7]
        
        if StepGoalSequenceBlock.objects.filter(cohort=cohort, when_used=None).exists():
            if StepGoalSequence_User.objects.filter(user=self.user).exists():
                sgsu = StepGoalSequence_User.objects.get(user=self.user)
                sgs = sgsu.step_goal_sequence
                return list(sgs.sequence_text.split(','))
            else:
                if not StepGoalSequence.objects.filter(cohort=cohort, is_used=False).exists():
                    # if there is no assigned StepGoalSequence
                    sgsb = StepGoalSequenceBlock.objects.filter(cohort=cohort, when_used=None).order_by('created').first()
                    
                    lines = sgsb.seq_block.split('\n')
                    
                    for index, line in lines.enumerate():
                        StepGoalSequence.objects.create(cohort=cohort, order=index + 1, sequence_text=line)
                        
                new_sequence = StepGoalSequence.objects.filter(cohort=cohort, is_used=False).order_by("order").first()
                new_sequence.is_used = True
                new_sequence.when_used = datetime.datetime.now()
                new_sequence.save()
                return list(new_sequence.sequence_text.split(','))    
        else:
            # if no seq block is set in db, use the default sequence
            EventLog.debug(self.user, "No StepGoalSequenceBlock is set in db. Using the default sequence: {}".format(default_seq))
            return default_seq

    def calculate_step_goals(self, startdate):
        # collecting evidences
        seq = self.get_seq()
        sgc_settings = StepGoalCalculationSettings.get(self.cohort)
        
        length = len(seq)
        enddate = startdate + timedelta(days=length-1)
        
        prev_enddate = startdate - timedelta(days=1)
        prev_startdate = startdate - timedelta(days=length)
        
        query_day = prev_startdate
        
        steps_log = []
        
        while query_day <= prev_enddate:
            steps_log_query = activity_summaries.models.Day.objects.filter(user=self.user, date=query_day).order_by('-updated')
            if steps_log_query.exists():
                steps_log.append(steps_log_query.first().steps)
            query_day += timedelta(days=1)
        
        if len(steps_log) == 0:
            # no day log is found
            base = 0
        else:
            # some log is found
            base = median(steps_log)
        
        # calculate step goals
        def cutoff(x, min, max):
            if x < min:
                return min
            if x > max:
                return max
            return x
        
        new_seq = [int(cutoff(x * sgc_settings.magnitude + base + sgc_settings.base_jump, sgc_settings.minimum, sgc_settings.maximum)) for x in seq]
        
        # look for the current evidence
        query = StepGoalsEvidence.objects.filter(user=self.user, startdate=startdate, enddate=enddate).order_by('-created')
        if query.exists():
            last_evidence = query.first()
            if last_evidence.enddate == enddate and \
                last_evidence.prev_startdate == prev_startdate and \
                last_evidence.prev_enddate == prev_enddate and \
                last_evidence.base == base and \
                last_evidence.magnitude == sgc_settings.magnitude and \
                last_evidence.base_jump == sgc_settings.base_jump and \
                last_evidence.maximum == sgc_settings.maximum and \
                last_evidence.minimum == sgc_settings.minimum and \
                last_evidence.evidence["seq"] == seq and \
                last_evidence.evidence["new_seq"] == new_seq:
                    # everything is same. skip insertion
                    return last_evidence
        
        # insert the evidence
        new_evidence = StepGoalsEvidence.objects.create(user=self.user,
                                                   startdate=startdate,
                                                   enddate=enddate,
                                                   prev_startdate = prev_startdate,
                                                   prev_enddate=prev_enddate,
                                                   base = base,
                                                   magnitude = sgc_settings.magnitude,
                                                   base_jump= sgc_settings.base_jump,
                                                   maximum = sgc_settings.maximum,
                                                   minimum = sgc_settings.minimum,
                                                   evidence={"seq": seq, "new_seq": new_seq, "steps_log": steps_log}
                                                   )
        
        # insert/update goals
        for day_index, goal_value in enumerate(new_seq):
            StepGoal.objects.create(user=self.user, date=startdate+timedelta(days=day_index), step_goal=goal_value)
        
        return new_evidence
        
    def get_goal(self, day):
        if not StepGoal.objects.filter(user=self.user, date=day).exists():
            # which is weird...
            EventLog.debug(self.user, "The day's step goal is not generated before. I'm generating it now...")
            update_goal(self.user.username)
        day_step_goal = StepGoal.objects.filter(user=self.user, date=day).order_by("-created").first().step_goal
        return day_step_goal
        
    
        
    # def create(self, date, message_framing=False):
    #     new_goal = StepGoal.objects.create(
    #         user = self.__user,
    #         date = date,
    #         step_goal = self.get_step_goal()
    #     )
    #     return new_goal

    # def generate_dump_goal_sequence(self, date=None):
    #     query = Participant.objects.filter(user=self.user)
    #     if query.exists():
    #         cohort = query.first().cohort
            
    #         PRBS_list = StepGoalPRBScsv.get_seq(cohort)
            
    #         base = self.get_median_steps(date=date)
            
    #         goal_sequence = [int(base + (self.magnitude * x)) for x in PRBS_list]
            
    #         return goal_sequence
    #     else:
    #         raise RuntimeError("No matching Participant for {}".format(self.user))
    
    # def get_median_steps(self, date=None):
    #     if date is None:
    #         day_service = DayService(self.user)
    #         date = day_service.get_current_date()
            
    #     steps_list = activity_summaries.models.Day.objects.filter(user=self.user, date__lte=date).order_by('-date').all()[:(self.number_of_previous_days)]
    #     ordered = sorted(steps_list, key=operator.attrgetter('steps'))
        
    #     len_steps_list = len(steps_list)
    #     if len_steps_list > 0:
    #         if len_steps_list % 2 == 0:
    #             half = int(len_steps_list / 2)
    #             median = int((ordered[half].steps + ordered[half+1].steps)/2)
    #         else:
    #             half = int((len_steps_list - 1)/ 2)
    #             median = ordered[half].steps
    #         return median
    #     else:
    #         raise RuntimeError("No Step Data")
    
    # def get_step_goal(self, date=None):
    #     """returns step goal

    #     Args:
    #         date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

    #     Returns:
    #         [int]: step goal of the day
    #     """
        
        
    #     try:
    #         goal = StepGoal.get(user=self.user, date=date)
    #         EventLog.info(self.user, "Returning goal: {}".format(goal))
    #         return goal
    #     except ValueError:
    #         median = self.get_median_steps(date=date)
    #         EventLog.info(self.user, "Step goal is not found. Calculating... date={}".format(date))
    #         prbs_list = self.generate_dump_goal_sequence(date=date)
    #         if date is None:
    #             day_service = DayService(user = self.user)
    #             date = day_service.get_current_date()
                
    #         for i in range(0, len(prbs_list)):
    #             StepGoal.objects.create(user=self.user, step_goal=prbs_list[i], date=(date + (timedelta(days=1) * i)))
            
    #         step_goal = StepGoal.objects.filter(user=self.user, date=date).first().step_goal
    #         EventLog.log(self.user, "Step goal could fetched and calculated correctly: {}".format(step_goal), EventLog.INFO)
    #         return step_goal

    # def get_heartsteps_step_goal(self, date=None):
    #     """returns step goal

    #     Args:
    #         date ([datetime], optional): date to fetch the step goal. Defaults to None. If omitted, today's goal is fetched

    #     Returns:
    #         [int]: step goal of the day
    #     """

    #     user = User.objects.get(self.__user.username)

    #     last_ten = activity_summaries.models.Day.objects.all().order_by('-date')[:10]
    #     ordered = sorted(last_ten, key=operator.attrgetter('steps'))
    #     serialized_step_counts = []

    #     all_days = activity_summaries.models.Day.objects.all().order_by('-date')
    #     index_of_today = len(all_days)

    #     with open('step-multipliers.csv', 'r') as csv_file:
    #         csv_reader = csv.DictReader(csv_file, delimiter=',')
    #         multipliers = list(csv_reader)

    #     multiplier = multipliers[index_of_today][1]

    #     if ordered:
    #         for step in ordered:
    #             serialized_step_counts.append({
    #                 'date': step.date.strftime('%Y-%m-%d'),
    #                 'steps': step.steps
    #             })

    #         new_goal = (serialized_step_counts[4]["steps"] + serialized_step_counts[5]["steps"])/2
    #         new_goal *= multiplier

    #         EventLog.log(user, "Step goal could fetched and calculated correctly.", EventLog.INFO)

    #         return new_goal
    #     else:
    #         EventLog.log(user, "Step goal could not be fetched. Ordered list could not be defined.", EventLog.ERROR)
    #         return None
