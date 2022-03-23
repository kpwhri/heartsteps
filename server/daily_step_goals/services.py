import datetime
import operator
import csv
from django.core.exceptions import ImproperlyConfigured
from statistics import median

from daily_step_goals.tasks import update_goal
import pytz
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
                return [float(x) for x in list(sgs.sequence_text.split(','))]
            else:
                if not StepGoalSequence.objects.filter(cohort=cohort, is_used=False).exists():
                    # if there is no assigned StepGoalSequence
                    sgsb = StepGoalSequenceBlock.objects.filter(cohort=cohort, when_used=None).order_by('when_created').first()
                    
                    lines = sgsb.seq_block.split('\n')
                    
                    for index, line in enumerate(lines):
                        StepGoalSequence.objects.create(cohort=cohort, order=index + 1, sequence_text=line)
                
                new_sequence = StepGoalSequence.objects.filter(cohort=cohort, is_used=False).order_by("order").first()
                new_sequence.is_used = True
                new_sequence.when_used = datetime.datetime.now().astimezone(pytz.utc)
                new_sequence.save()
                
                StepGoalSequence_User.objects.create(user=self.user, step_goal_sequence=new_sequence)
                
                return [float(x) for x in list(new_sequence.sequence_text.split(','))]
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
            base = 2000
            sgc_settings.magnitude = 0
            sgc_settings.base_jump = 0
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
        
        safe_base = cutoff(base, sgc_settings.minimum, sgc_settings.maximum)
        new_seq = [int(x * sgc_settings.magnitude + safe_base + sgc_settings.base_jump) for x in seq]
        # old way:
        # new_seq = [int(cutoff(x * sgc_settings.magnitude + base + sgc_settings.base_jump, sgc_settings.minimum, sgc_settings.maximum)) for x in seq]
        
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
            update_goal(self.user.username, day=day)
        day_step_goal = StepGoal.objects.filter(user=self.user, date=day).order_by("-created").first().step_goal
        return day_step_goal