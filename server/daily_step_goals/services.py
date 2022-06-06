import datetime
import operator
import csv
from django.core.exceptions import ImproperlyConfigured
from statistics import median

import daily_step_goals as dsg
import pytz
from push_messages.services import PushMessageService

from surveys.serializers import SurveyShirinker
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
            EventLog.error(self.user, "No StepGoalSequenceBlock is set in db. Using the default sequence: {}".format(default_seq))
            return default_seq

    def calculate_step_goals(self, startdate):
        calc_log = []

        # collecting evidences
        calc_log.append("Checking sequence...")
        seq = self.get_seq()
        calc_log.append("Sequence: {}".format(seq))
        sgc_settings = StepGoalCalculationSettings.get(self.cohort)
        calc_log.append("StepGoalCalculationSettings: {}".format(sgc_settings.__dict__))
        
        length = len(seq)
        calc_log.append("Sequence length: {}".format(length))
        enddate = startdate + timedelta(days=length-1)
        calc_log.append("Start date: {}, end date: {}".format(startdate, enddate))
        
        prev_enddate = startdate - timedelta(days=1)
        prev_startdate = startdate - timedelta(days=length)
        calc_log.append("Previous start date: {}, previous end date: {}".format(prev_startdate, prev_enddate))

        query_day = prev_startdate
        
        steps_list = []
        
        calc_log.append("Entering the loop...")
        while query_day <= prev_enddate:
            calc_log.append("   Checking {}".format(query_day))
            steps_log_query = activity_summaries.models.Day.objects.filter(user=self.user, date=query_day).order_by('-updated')
            if steps_log_query.exists():
                steps_list.append(steps_log_query.first().steps)
                calc_log.append("      {} has been found in the database".format(query_day))
            query_day += timedelta(days=1)
        
        calc_log.append("Steps list: {}".format(steps_list))
        if len(steps_list) == 0:
            # no day log is found
            calc_log.append("No day log is found. Setting as defaults...")
            base = 2000
            sgc_settings.magnitude = 0
            sgc_settings.base_jump = 0
            calc_log.append("Base: {}, magnitude: {}, base_jump: {}".format(base, sgc_settings.magnitude, sgc_settings.base_jump))
        else:
            # some log is found
            base = median(steps_list)
            calc_log.append("Base: {}".format(base))
        
        # calculate step goals
        def cutoff(x, min, max):
            #print("x({}): {}, min({}): {}, max({}): {}".format(type(x), x, type(min), min, type(max), max))
            if x < min:
                return min
            if x > max:
                return max
            return x
        
        #print("Calculating step goals...: sgc_settings: {}".format(sgc_settings.__dict__))
        safe_base = cutoff(base, sgc_settings.minimum, sgc_settings.maximum)
        calc_log.append("Safe base: {}".format(safe_base))
        new_seq = [int(x * sgc_settings.magnitude + safe_base + sgc_settings.base_jump) for x in seq]
        calc_log.append("New sequence: {}".format(new_seq))
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
                last_evidence.freetext == "\n".join(calc_log) and \
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
                                                   freetext = "\n".join(calc_log),
                                                   evidence={"seq": seq, "new_seq": new_seq, "steps_log": calc_log}
                                                   )
        
        # insert/update goals
        for day_index, goal_value in enumerate(new_seq):
            StepGoal.objects.create(user=self.user, date=startdate+timedelta(days=day_index), step_goal=goal_value)
        
        return new_evidence
        
    def get_goal(self, day):
        if not StepGoal.objects.filter(user=self.user, date=day).exists():
            # which is weird...
            EventLog.info(self.user, "The day's step goal is not generated before. I'm generating it now...")
            dsg.tasks.update_goal(self.user.username, day=day)
        # day_step_goal = StepGoal.objects.filter(user=self.user, date=day).order_by("-created").first().step_goal
        day_step_goal = StepGoal.get(self.user, day)
        return day_step_goal