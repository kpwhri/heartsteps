from datetime import datetime, timedelta, date, time
import pytz
import math
import uuid
import ast
import operator as op

from django.db import models, IntegrityError

from django.contrib.auth import get_user_model
# from django_celery_beat.models import PeriodicTask, PeriodicTasks
from daily_tasks.models import DailyTask
from days.services import DayService
from surveys.models import Answer, Question, Survey, SurveyAnswer, SurveyQuerySet, SurveyQuestion
from .constants import TASK_CATEGORY
from django.db import models

from user_event_logs.models import EventLog
from participants.models import Cohort, Participant
from daily_step_goals.services import StepGoalsService
from activity_summaries.models import Day
import random

from fitbit_api.models import FitbitAccountUser
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.services import FitbitStepCountService
from push_messages.models import Message

User = get_user_model()

class Configuration(models.Model):
    user = models.OneToOneField(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )
    enabled = models.BooleanField(default = True)
    
    @property
    def last_survey(self):
        if not hasattr(self, '_last_survey'):
            self._last_survey = self.get_last_survey()
        return self._last_survey

    @property
    def last_answered_survey(self):
        if not hasattr(self, '_last_answered_survey'):
            self._last_answered_survey = self.get_last_answered_survey()
        return self._last_answered_survey

    @property
    def summary_of_last_24_hours(self):
        if not hasattr(self, '_summary_of_last_24_hours'):
            self._summary_of_last_24_hours = self.get_summary_of_last_24_hours()
        return self._summary_of_last_24_hours

    @property
    def summary_of_last_7_days(self):
        if not hasattr(self, '_summary_of_last_7_days'):
            self._summary_of_last_7_days = self.get_summary_of_last_7_days()
        return self._summary_of_last_7_days

    def get_last_survey(self):
        activity_survey = BoutPlanningSurvey.objects.filter(
            user = self.user
        ).order_by('created') \
        .last()
        return activity_survey

    def get_last_answered_survey(self):
        activity_survey = BoutPlanningSurvey.objects.filter(
            user = self.user,
            answered = True
        ).order_by('created') \
        .last()
        return activity_survey
        
class BoutPlanningSurveyQuestion(Question):
    pass

class BoutPlanningSurvey(Survey):
    QUESTION_MODEL = BoutPlanningSurveyQuestion
    
    objects = SurveyQuerySet.as_manager()

class JustWalkJitaiDailyEmaQuestion(Question):
    pass

class JustWalkJitaiDailyEma(Survey):
    QUESTION_MODEL = JustWalkJitaiDailyEmaQuestion
    
    objects = SurveyQuerySet.as_manager()



def eval_(node):
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg, ast.Mod: op.mod, ast.Eq: op.eq,
             ast.Lt: op.lt, ast.Gt: op.gt, ast.LtE: op.le, 
             ast.GtE: op.ge}
    
    allowed_functions = ["int"]
    
    def power(a, b):
        if any(abs(n) > 100 for n in [a, b]):
            raise ValueError((a,b))
        return op.pow(a, b)
    
    operators[ast.Pow] = power
    
    if isinstance(node, list):
        if len(node) == 1:
            return eval_(node[0])
        else:
            raise ValueError(str(node))
    elif isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.Compare):
        is_true = True
        
        if isinstance(node.ops, list):
            for i, i_op in enumerate(node.ops):
                is_true = is_true and operators[type(i_op)](eval_(node.left), eval_(node.comparators[i]))
        else:
            is_true = is_true and operators[type(node.ops)](eval_(node.left), eval_(node.comparators))
        return is_true
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    elif isinstance(node, ast.Call):
        if node.func.id in allowed_functions:
            args_list = [eval_(x) for x in node.args]
            
            function_str = "{}({})".format(node.func.id, ", ".join([str(x) for x in args_list]))
            value = eval(function_str)
            
            return value
        else:
            raise ValueError("Not allowed function: {}".format(node.func.id))
    elif isinstance(node, ast.Expr):
        return eval_(node.value)
    else:
        raise TypeError(node)

def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)

def replace_special_variables(expr, parameters):
    new_expr = expr
    
    # Day of week
    if "today" in parameters:
        import calendar
        today_weekday = parameters["today"].weekday()
        yesterday_weekday = (today_weekday - 1) % 7
        tomorrow_weekday = (today_weekday + 1) % 7
        new_expr = new_expr.replace("${DAY_OF_WEEK}", calendar.day_name[today_weekday])
        new_expr = new_expr.replace("${DAY_OF_WEEK:TODAY}", calendar.day_name[today_weekday])
        new_expr = new_expr.replace("${DAY_OF_WEEK:TOMORROW}", calendar.day_name[tomorrow_weekday])
        new_expr = new_expr.replace("${DAY_OF_WEEK:YESTERDAY}", calendar.day_name[yesterday_weekday])

        # Number of Days since the study started
        enrolled_date = Participant.objects.filter(user=parameters["user"]).order_by("study_start_date").first().study_start_date
        new_expr = new_expr.replace("${DAYS_SINCE_ENROLLED}",
                                    str((parameters["today"] - enrolled_date).days)
                                    )
    
    return new_expr
    
class JSONSurvey(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, default="")
    structure = models.JSONField(null=False, default=dict)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    
    
    
    def traverse(self, item_name, parameters=None):
        item = self.item_bank[item_name]
        assert type(item) is dict, "item should be a dictionary."
        
        if parameters is None and item["type"] in ("shown if true", "single"):
            parameters = {"user": self.user}
            day_service = DayService(user=self.user)
            parameters["today"] = day_service.get_current_date()
        
        if item["type"] == "list":
            for subitem in item["items"]:
                self.traverse(subitem, parameters)
        elif item["type"] == "alternating":
            last_item_index = self.get_last_item_index(item_name)
            current_item_index = (last_item_index + 1) % len(item["options"])
            self.insert_last_item_index(item_name, current_item_index)
            self.traverse(item["options"][current_item_index], parameters)
        elif item["type"] == "shown if true":
            condition_str = replace_special_variables(item["condition expression"], parameters)
            print("condition expression: {}".format(condition_str))
            if eval_expr(condition_str) == True:
                self.traverse(item["item"], parameters)
        elif item["type"] == "single":
            final_item = {
                    "name": item_name,
                    "text": replace_special_variables(item["text"], parameters),
                    "response_type": item["response_type"]
                }
            self.items_list.append(final_item)
        else:
            raise ValueError("Not supported item type: {}-{}".format(item_name, item))
    
    def get_last_item_index(self, item_name):
        query = LastItemLog.objects.filter(jsonsurvey=self, item_name=item_name, user=self.user)
        
        if query.exists():
            return query.order_by("-created").first().used_index
        else:
            return -1
        
    def insert_last_item_index(self, item_name, item_index):
        LastItemLog.objects.create(jsonsurvey=self, item_name=item_name, user=self.user, used_index=item_index)
    
    def insert_or_update_question_and_answers(self):
        self.question_obj_list = []
        
        for index, item in enumerate(self.items_list):
            question_found = False
            response_info = self.response_bank[item["response_type"]]
            query = Question.objects.filter(label=item["text"])
            if query.exists():
                for question in query.all():
                    answer_count = Answer.objects.filter(label__in=response_info["answers"], question=question).count()
                    
                    if answer_count == len(response_info["answers"]) and question.kind == response_info["type"]:
                        self.question_obj_list.append(question)
                        question_found = True
                        break
            
            if not question_found:
                question_obj = Question.objects.create(name=uuid.uuid4(), 
                                        label=item["text"],
                                        description='',
                                        order=index,
                                        kind=response_info["type"]
                                        )
                
                for answer_index, answer in enumerate(response_info["answers"]):
                    Answer.objects.create(label=answer,
                                          value=answer_index,
                                          question=question_obj,
                                          order=answer_index)
                self.question_obj_list.append(question_obj)
        
                
        
    def substantiate(self, user, parameters=None):
        from pprint import pprint
        self.user = user
        self.items_list = []
        
        self.traverse(self.root_item, parameters)
        self.insert_or_update_question_and_answers()
        
        new_survey = Survey.objects.create(user=user)
        
        for question_index, question_obj in enumerate(self.question_obj_list):
            new_survey_question = SurveyQuestion.objects.create(name="{}-{}".format(self.name, question_index),
                                          label=question_obj.label,
                                          description=question_obj.description,
                                          question=question_obj,
                                          survey=new_survey,
                                          order=question_index,
                                          kind=question_obj.kind)
            query = Answer.objects.filter(question=question_obj).order_by("order")
            for answer_index, answer_obj in enumerate(list(query.all())):
                SurveyAnswer.objects.create(label=answer_obj.label,
                                            value=answer_obj.value,
                                            question=new_survey_question,
                                            answer=answer_obj,
                                            order=answer_index)
        
        return new_survey
    
    @property
    def meta(self):
        return self.structure["meta"]
    
    @property
    def version(self):
        return self.meta["syntax version"]
    
    @property
    def response_bank(self):
        return self.structure["response bank"]
    
    @property
    def item_bank(self):
        return self.structure["item bank"]
    
    @property
    def root_item(self):
        return self.structure["root item"]

class LastItemLog(models.Model):
    jsonsurvey = models.ForeignKey(JSONSurvey, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    used_index = models.IntegerField(null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class BoutPlanningMessage(models.Model):
    message = models.TextField(blank=True, null=True)

class BoutPlanningNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey('Level', on_delete=models.CASCADE, null=True, blank=True)
    decision = models.ForeignKey('BoutPlanningDecision',
                                 on_delete=models.CASCADE, null=True, blank=True)
    when = models.DateTimeField(auto_now_add=True)

    def create(user, message, level, decision):
        day_service = DayService(user)
        current_time = day_service.get_current_datetime()

        BoutPlanningNotification.objects.create(user=user,
                                            message=message,
                                            level=level,
                                            decision=decision,
                                            when=current_time)


class FirstBoutPlanningTime(models.Model):
    class FirstBoutPlanningTimeExistException(Exception):
        pass

    class FirstBoutPlanningTimeDoNotExistException(Exception):
        pass

    class NoSuchUserException(Exception):
        pass

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    hour = models.IntegerField(default=7)
    minute = models.IntegerField(default=0)

    active = models.BooleanField(default=True)

    def __str__(self):
        if self.active:
            return "FirstBoutPlanningTime = {} ({})".format(
                self.time, self.user)
        else:
            return "Not active ({})".format(self.user)

    @property
    def time(self):
        return "{:02}:{:02}".format(self.hour, self.minute)

    @property
    def data_dict(self):
        return {'time': self.time}

    def __is_formatted_properly(time):
        assert isinstance(time, str), "time must be a string"

        try:
            FirstBoutPlanningTime.__parse(time)
            return True
        except:
            return False

    def __parse(time):
        assert isinstance(time, str), "time must be a string"
        time_list = time.split(':')
        if len(time_list) != 2:
            raise ValueError("wrong time string: {}".format(time))
        try:
            hour = int(time_list[0])
            minute = int(time_list[1])

            if hour in range(0, 24) and minute in range(0, 60):
                return (hour, minute)
            else:
                raise ValueError("wrong time string: {}".format(time))
        except:
            raise ValueError("wrong time string: {}".format(time))

    def convert_to_user_obj(user):
        if isinstance(user, str):
            try:
                user_obj = User.objects.get(username=user)
            except User.DoesNotExist:
                raise FirstBoutPlanningTime.NoSuchUserException
        elif isinstance(user, User):
            user_obj = user
        else:
            assert isinstance(
                user, User
            ), "user argument should be an instance of User class: {}".format(
                type(user))
        return user_obj

    def __get_base_query(user):
        """returns the base query of the FirstBoutPlaningTime object"""

        return FirstBoutPlanningTime.objects.filter(user=user, active=True)

    def exists(user):
        """check if the first bout planning time exists

        Args:
            user (User or str)
            
        Raises:
            FirstBoutPlanningTime.NoSuchUserException : if the username is wrong

        Returns:
            boolean: if the first bout planning time exist
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)

        return FirstBoutPlanningTime.__get_base_query(user_obj).exists()

    def create(user, time="07:00"):
        """Create a new first bout planning time.
        
        Arguments: 
            user(User or str)
            time(str) optional
        
        Raises:
            FirstBoutPlanningTime.FirstBoutPlanningTimeExistException : if the first bout planning time exists
            FirstBoutPlanningTime.NoSuchUserException : if the username is wrong
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)
        assert isinstance(time,
                          str), "time argument should be a string: {}".format(
                              type(time))
        assert FirstBoutPlanningTime.__is_formatted_properly(
            time), "time should be correctly formated: {}".format(time)

        (hour, minute) = FirstBoutPlanningTime.__parse(time)

        if FirstBoutPlanningTime.exists(user_obj):
            raise FirstBoutPlanningTime.FirstBoutPlanningTimeExistException

        return FirstBoutPlanningTime.objects.create(user=user_obj,
                                                    hour=hour,
                                                    minute=minute)

    def update(user: User, time: str):
        """updates if the first bout planning time exists

        Args:
            user (User or str)
            time (str): new time

        Raises:
            FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException: if the featureFlags do not exist
            FirstBoutPlanningTime.NoSuchUserException: if the user does not exist

        Returns:
            FirstBoutPlanningTime object: updated first bout planning time
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)
        assert isinstance(time,
                          str), "time argument should be a string: {}".format(
                              type(time))
        assert FirstBoutPlanningTime.__is_formatted_properly(
            time), "time should be correctly formated: {}".format(time)

        if not FirstBoutPlanningTime.exists(user_obj):
            raise FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException

        (hour, minute) = FirstBoutPlanningTime.__parse(time)

        obj = FirstBoutPlanningTime.get(user_obj)
        obj.hour = hour
        obj.minute = minute
        obj.save()

        return obj

    def get(user: User):
        """tries to get the first bout planning time 

        Args:
            user (User or str)

        Raises:
            FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException: if the first bout planning time do not exist.
            FirstBoutPlanningTime.NoSuchUserException : if the username is wrong
            
        Returns:
            FeatureFlag object
        """
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)

        if not FirstBoutPlanningTime.exists(user_obj):
            raise FirstBoutPlanningTime.FirstBoutPlanningTimeDoNotExistException

        return FirstBoutPlanningTime.__get_base_query(user_obj).get()

    def get_daily_tasks(user):
        """This will fetch all daily tasks for the user.
        
        Returns:
            DailyTask[]
        """

        # It converts username to user object (if provided) If User object is provided, it will return the user itself.
        user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)

        task_list = DailyTask.objects.filter(user=user_obj, category=TASK_CATEGORY).order_by("day", "hour", "minute")

        return list(task_list)


class Level(models.Model):

    RECOVERY = 'RE'
    RANDOM = 'RA'
    NO = 'NO'
    NR = 'NR'
    FULL = 'FU'

    DEFAULT = FULL

    LEVELS = [
        (RECOVERY, 'RE'),
        (RANDOM, 'RA'),
        (NO, 'NO'),
        (NR, 'NR'),
        (FULL, 'FU'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVELS)
    date = models.DateField()

    def __str__(self):
        return "{} @ {}".format(self.level, self.date)

    def bulk_create(user, levels, start_date):
        obj_list = []
        current_date = start_date
        for level in levels:
            obj = Level()
            obj.user=user
            obj.level=level
            obj.date=current_date
            current_date += timedelta(days=1)
            obj_list.append(obj)
        Level.objects.bulk_create(obj_list)
        
    def create(user: User, level: str, date=None):
        """Create a new Level"""
        if date is None:
            day_service = DayService(user)

            # what date is it now there?
            date = day_service.get_current_date()
        if Level.exists(user, date):
            raise IntegrityError('Level already exists')
        else:
            return Level.objects.create(user=user, date=date, level=level)

    def get(user, date=None):
        """Get a Level object"""
        EventLog.debug(user, "get({}) is called".format(date))
        if date is None:
            day_service = DayService(user)

            # what date is it now there?
            date = day_service.get_current_date()

        if Level.exists(user, date):
            return_object = Level.objects.get(user=user, date=date)
        else:
            return_object = Level.objects.create(user=user,
                                                 date=date,
                                                 level=Level.DEFAULT)
        EventLog.debug(user, "get({}) returns: {}".format(date, return_object))

        return return_object

    def exists(user, date):
        """Check if the Level object"""
        return Level.objects.filter(user=user, date=date).exists()


def ifthisthenthat(this, that, it):
    if this:
        return that
    else:
        return it


def force_str(obj):
    if isinstance(obj, str):
        return "\"{}\"".format(obj)
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, list):
        return "[{}]".format(",".join(list(map(lambda x: force_str(x), obj))))
    elif isinstance(obj, dict):
        return "{{{}}}".format(",".join(
            list(map(lambda x: "\"{}\": {}".format(x, force_str(obj[x])),
                     obj))))
    else:
        return str(obj)

def find_consecutive_active_mins(step_list, active=60, mins=5):
    cursor = 0
    cumulative_sum = 0
    for i in range(len(step_list)):
        if step_list[i] >= active:
            cumulative_sum += 1
            if cumulative_sum == mins:
                return cursor
            else:
                pass
        else:
            cumulative_sum = 0
            cursor = i + 1
    
    return None # no cumulative active minutes are found

# class RandomDecision(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     random_value = models.FloatField(blank=True, null=True)
#     return_bool = models.BooleanField(null=True, default=None)

#     def create(user):
#         obj = RandomDecision.objects.create(user=user,
#                                             random_value=random.random())
#         return obj

#     def decide(self):
#         self.return_bool = (self.random_value < 0.5)
#         self.save()
#         return self.return_bool


class BoutPlanningDecision(models.Model):
    WEEKDAY_WEEKEND = 'weekday/weekend'
    DAY_BY_DAY = 'day by day'
    DAY_OF_A_WEEK = 'day of a week'

    RANDOM_CRITERIA = 0.5
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    N = models.BooleanField(null=True, default=None)
    O = models.BooleanField(null=True, default=None)
    R = models.BooleanField(null=True, default=None)
    return_bool = models.BooleanField(null=True, default=None)
    data = models.JSONField(null=True, default=None)
    when_created = models.DateTimeField(auto_now_add=True,
                                        null=True,
                                        blank=True)
        
    def create(user):
        obj = BoutPlanningDecision.objects.create(user=user, data={})
        return obj

    def add_line(self, line):
        if "lines" in self.data:
            self.data["lines"].append(line)
        else:
            self.data["lines"] = [line]

    def apply_random(self):
        self.add_line("  apply_random() starting")
        random_value = random.random()
        self.data['random_value'] = random_value
        self.add_line("    random_value is {} and RANDOM_CRITERIA is {}.".format(random_value, BoutPlanningDecision.RANDOM_CRITERIA))
        
        self.return_bool = random_value < BoutPlanningDecision.RANDOM_CRITERIA
        self.add_line("    returning {}...".format(self.return_bool))
        self.save()
        
    def apply_N(self):
        self.add_line("  apply_N() starting")
        decision_point_index = self.__get_decision_point_index()
        self.add_line("    This is decision point #{}.".format(decision_point_index))
        self.data['decision_point_index'] = decision_point_index

        day_service = DayService(user=self.user)
        today = day_service.get_current_date()
        self.add_line("    Today is {}".format(force_str(today)))
        yesterday = today - timedelta(days=1)
        self.add_line("    Yesterday is {}".format(force_str(yesterday)))
        self.data['today'] = force_str(today)
        self.data['yesterday'] = force_str(yesterday)
        step_goals_service = StepGoalsService(self.user)

        if decision_point_index == 0:
            self.add_line("      Since the decision point index is 0,")
            yesterday_step_goal = step_goals_service.get_goal(yesterday)
            self.add_line("        Yesterday's step goal was {}.".format(yesterday_step_goal))
            self.data['yesterday_step_goal'] = yesterday_step_goal

            yesterday_activity_summary = Day.get(user=self.user,
                                                 date=yesterday)
            if yesterday_activity_summary:
                yesterday_step_count = yesterday_activity_summary.steps
            else:
                self.add_line("        (Weirdly, yesterday's activity summary was not found.)")
                yesterday_step_count = 0
            self.add_line("        Yesterday's step count was {}.".format(yesterday_step_count))
            self.data['yesterday_step_count'] = yesterday_step_count

            if yesterday_step_goal <= yesterday_step_count:
                self.add_line("    Since the user walked more than the goal yesterday, N of 1st decision point is false.")
                self.N = False
            else:
                self.add_line("    Since the user walked less than the goal yesterday, N of 1st decision point is true.")
                self.N = True
        else:
            self.add_line("      Since the decision point index is not 0,")
            today_step_goal = step_goals_service.get_goal(today)
            self.add_line("        Today's step goal is {}.".format(today_step_goal))
            self.data['today_step_goal'] = today_step_goal

            prorated_today_step_goal = today_step_goal * (
                decision_point_index * 3) / 12
            
            self.data['prorated_today_step_goal'] = prorated_today_step_goal
            self.add_line("        Today's prorated step goal is {}.".format(prorated_today_step_goal))

            # TODO: Check if this works during the day
            today_activity_summary = Day.get(user=self.user, date=today)
            if today_activity_summary:
                today_step_count = today_activity_summary.steps
            else:
                self.add_line("        (Weirdly, today's activity summary was not found.)")
                today_step_count = 0
            self.add_line("        Today's current step count is {}.".format(today_step_count))            
            self.data['today_step_count'] = today_step_count

            if prorated_today_step_goal <= today_step_count:
                self.add_line("    Since the user walked more than the prorated goal as of now, N of 1st decision point is false.")
                self.N = False
            else:
                self.add_line("    Since the user walked less than the prorated goal as of now, N of 1st decision point is true.")
                self.N = True

        self.save()

    def apply_O(self):
        self.add_line("  apply_O() starting")
        criteria = [{
            'walk_heuristic': 60,
            'minimum': 0,
            'maximum': 7,
            'mode': BoutPlanningDecision.WEEKDAY_WEEKEND,
            'fetch_period': 3,
            'window_size': 3,
            'threshold1': 0.55,
            'threshold2': 0.5
        }, {
            'walk_heuristic': 60,
            'minimum': 8,
            'maximum': 21,
            'mode': BoutPlanningDecision.WEEKDAY_WEEKEND,
            'fetch_period': 8,
            'window_size': 3,
            'threshold1': 0.55,
            'threshold2': 0.6
        }, {
            'walk_heuristic': 60,
            'minimum': 22,
            'maximum': 9999,
            'mode': BoutPlanningDecision.DAY_BY_DAY,
            'fetch_period': 5,
            'window_size': 3,
            'threshold1': 0.55,
            'threshold2': 0.55
        }]

        study_day_index = self.__get_study_day_index()
        self.add_line("    Today's study day index is {}".format(study_day_index))
        self.data['study_day_index'] = study_day_index

        criterion = self.__get_criterion(study_day_index, criteria)
        self.add_line("    Today's criterion is recorded in data dictionary")
        self.data['criterion'] = criterion

        fetch_periods = self.__get_fetch_periods(study_day_index, criterion)
        self.add_line("    The following dates are used for O calculation: {}".format(fetch_periods))
        self.data['fetch_periods'] = force_str(fetch_periods)

        walkdata_list = self.__fetch_walkdata(fetch_periods, criterion)
        self.O = self.__process_walkdata(criterion, walkdata_list)
        self.add_line("    O is calculated with the criteria and walkdata: {}".format(self.O))

        self.save()

    def apply_R(self):
        self.add_line("  apply_R() starting")
        def fetch_bout_planning_notification_logs(days=3):
            when_startpoint = datetime.now() - timedelta(
                days=days)
            query = BoutPlanningNotification.objects.filter(
                user=self.user, when__gte=when_startpoint).order_by('when')

            return [{"when": x.when} for x in query]
        
        def is_notification_sent_at_last_decision_point():
            query = BoutPlanningDecision.objects.filter(user=self.user).order_by('-when_created')
            
            if query.exists():
                return query.first().return_bool
            else:
                return False
            
        def favorable_response_in(howlong):
            logs = fetch_bout_planning_notification_logs(days=1)
            step_count_service = FitbitStepCountService(self.user)

            for log in logs:
                starttime = log["when"]
                endtime = starttime + timedelta(minutes=180)
                
                step_list = step_count_service.get_all_step_data_list_between(starttime, endtime)
                
                if find_consecutive_active_mins(step_list, active=60, mins=5):
                    return True
            
            return False
        
        budget = 0.5  # 50% of decision points
        self.data['budget'] = budget
        self.add_line("    Using budget of {}.".format(budget))

        last_decision_point_result = is_notification_sent_at_last_decision_point()
        if last_decision_point_result:
            self.add_line("    For the last decision point, the notification is sent.")
        else:
            self.add_line("    For the last decision point, the notification is not sent.")
        self.data['last_decision_point_result'] = last_decision_point_result

        logs = fetch_bout_planning_notification_logs()
        self.add_line("    During the last 3 days, the following notifications are sent: {}".format([x["when"] for x in logs]))
        self.data['logs'] = logs

        if len(logs) < budget * 12:  # under budget
            self.add_line("    Only {} notifications are sent, it is under budget.".format(len(logs)))
            if last_decision_point_result == True:
                self.add_line("    Since the notification is sent at the last decision point, the notification will not be sent. (R=False)")
                self.R = False
            else:
                self.add_line("    Since the notification is not sent at the last decision point, the notification will be sent. (R=True)")
                self.R = True
        else:
            self.add_line("    {} notifications are sent, it is over budget. Thus, if there's a favorable response during last 24 hours is calculated.".format(len(logs)))
            condition1 = favorable_response_in(timedelta(hours=24))
            if condition1:
                self.add_line("    During last 24 hours, at least one notification is responded favorably.")
            else:
                self.add_line("    During last 24 hours, no notification is responded favorably.")
            condition2 = (last_decision_point_result == False)
            if condition2:
                self.add_line("    At the last decision point, notification is not sent.")
            else:
                self.add_line("    At the last decision point, notification is sent.")
            

            if condition1 and condition2:
                self.add_line("    During last 24 hours, at least one notification is responded favorably and at the last decision point, notification is not sent, R is true")
                self.R = True
            else:
                self.add_line("    During last 24 hours, no notification is responded favorably or at the last decision point, notification is sent, R is false")
                self.R = False
        self.save()

    def decide(self):
        self.add_line("  decide() starting")
        if self.N is None and self.O is None and self.R is None and self.return_bool is not None:
            return self.return_bool
        else:
            self.return_bool = True
            if self.N is not None:
                self.return_bool = self.return_bool & self.N
            if self.O is not None:
                self.return_bool = self.return_bool & self.O
            if self.R is not None:
                self.return_bool = self.return_bool & self.R

            self.save()
            return self.return_bool

    def __get_user_local_time(self):
        day_service = DayService(self.user)
        user_local_time = day_service.get_current_datetime()
        return user_local_time

    def __get_decision_point_index(self):
        user_local_time = self.__get_user_local_time()
        self.data['user_local_time'] = force_str(user_local_time)
        first_bout_planning_time_obj = FirstBoutPlanningTime.get(self.user)
        diff_in_minutes = (user_local_time.hour * 60 + user_local_time.minute
                           ) - first_bout_planning_time_obj.hour * 60
        diff_by_three_hours = int(round(diff_in_minutes / 180, 0))

        if diff_by_three_hours >= 0 and diff_by_three_hours < 4:
            decision_point_index = diff_by_three_hours
        else:
            raise RuntimeError(
                "Unusual time diff: user_local[{}], first_hour[{}]".format(
                    user_local_time, first_bout_planning_time_obj))

        return decision_point_index

    def __get_study_day_index(self):
        def get_study_start_date():
            participant = Participant.objects.filter(user=self.user)
            if participant and participant.exists():
                return participant.first().study_start_date
            else:
                raise ValueError("No Participant under user: {}".format(
                    self.user))

        study_start_date = get_study_start_date()
        user_local_date = self.__get_user_local_time().date()

        date_diff = user_local_date - study_start_date

        return date_diff.days

    def __get_criterion(self, study_day_index, criteria):
        for criterion in criteria:
            if 'minimum' in criterion:
                if criterion['minimum'] > study_day_index:
                    continue
            if 'maximum' in criterion:
                if criterion['maximum'] < study_day_index:
                    continue

            # returning a new copy in the memory of the criterion
            return dict(criterion)
        raise ValueError(
            "Could not find criterion that matches study_day_index: {}".format(
                study_day_index))

    def __get_fetch_periods(self, study_day_index, criterion):
        """returns the list of dates to fetch step data depending on how long it has been since the start of the study

        Args:
            study_day_index (int): how long it has been since the start of the study
            criterion (dictionary): opportunity condition criterion parameter
        """
        def is_weekend(a_day):
            """return if the date is a weekend

            Args:
                a_day (date): a date to check

            Returns:
                boolean: True if the date is weekend
            """
            return a_day.weekday() in (5, 6)

        def always_true(_):
            return True

        def get_weekday(date):
            return date.weekday()

        user_local_date = self.__get_user_local_time().date()

        days_list = []
        date_cursor = user_local_date - timedelta(days=1)

        if 'fetch_period' in criterion:
            if criterion['mode'] == BoutPlanningDecision.WEEKDAY_WEEKEND:
                diag_fx = is_weekend
            elif criterion['mode'] == BoutPlanningDecision.DAY_BY_DAY:
                diag_fx = always_true
            elif criterion['mode'] == BoutPlanningDecision.DAY_OF_A_WEEK:
                diag_fx = get_weekday
            else:
                raise ValueError("Unknown criterion mode: {}".format(
                    criterion['mode']))

            reference_value = diag_fx(user_local_date)

            while True:
                if diag_fx(date_cursor) == reference_value:
                    days_list.append(date_cursor)
                if len(days_list) == criterion['fetch_period']:
                    break
                if len(days_list) > 99:  # it is fetching too many days
                    raise ValueError(
                        'fetch_period should be lower than 99: {}'.format(
                            criterion['fetch_period']))
                date_cursor = date_cursor - timedelta(days=1)
        else:
            raise ValueError('fetch_period must be in the criteria')

        return days_list

    def __fetch_walkdata(self, fetch_periods, criterion):
        def fetch_walkdata(criterion, date=None):
            day_service = DayService(self.user)
            step_count_service = FitbitStepCountService(self.user)

            step_data_list = step_count_service.get_all_step_data_list_between(
                day_service.get_start_of_day(date),
                day_service.get_end_of_day(date))

            for i in range(0, len(step_data_list)):
                step_data_list[i] = ifthisthenthat(
                    step_data_list[i] > criterion['walk_heuristic'], 1, 0)

            return step_data_list

        raw_walk_data = []
        for a_day in fetch_periods:
            raw_walk_data.append({
                'date': a_day,
                'raw_data': fetch_walkdata(criterion, a_day)
            })

        return raw_walk_data

    def __process_walkdata(self, criterion, walkdata_list):
        def calculate_moving_average(criterion, padded_walkdata):
            half_window_size = criterion['window_size']
            window_size = half_window_size * 2 + 1
            # average should be over threshold1. instead of dividing
            # by window size, the threshold is pre-calculated for the speed
            threshold1 = criterion['threshold1'] * window_size

            moving_averaged_walkdata = [0] * 1440
            # for time complexity of O(n), moving average became more complex
            current_sum = sum(padded_walkdata[0:window_size])
            moving_averaged_walkdata[half_window_size - 1] = ifthisthenthat(
                current_sum > threshold1, 1, 0)

            for i in range(half_window_size, 1440 - half_window_size):
                current_sum = current_sum + padded_walkdata[
                    i + half_window_size -
                    1] - padded_walkdata[i - half_window_size]
                moving_averaged_walkdata[i] = ifthisthenthat(
                    current_sum > threshold1, 1, 0)

            return moving_averaged_walkdata

        activity_list = []

        # 0. Prepare to Pick the right 3-hour window
        decision_point_index = self.__get_decision_point_index()

        first_bout_planning_time = FirstBoutPlanningTime.get(self.user).hour
        self.data['first_bout_planning_time'] = first_bout_planning_time

        start_index = int(
            (first_bout_planning_time + decision_point_index * 3) * 60)
        self.data['start_index'] = start_index
        finish_index = start_index + 180
        self.data['finish_index'] = finish_index

        # 1. padding with zeros, reorganizing overlapped step data
        # sometimes, Fitbit overlapses/jump minute step data when the timezone changes
        for walkdata in walkdata_list:
            # padded_walkdata = self.__pad_walkdata(walkdata['raw_data'])
            padded_walkdata = walkdata['raw_data']

            # 2. moving-averaging and applying threshold 1
            moving_averaged_walkdata = calculate_moving_average(
                criterion, padded_walkdata)

            # 3. Pick up proper timespan, check if there's an activity
            if_activity_exists = max(
                moving_averaged_walkdata[start_index:finish_index])
            activity_list.append(if_activity_exists)

        # print('activity_list: {}'.format(activity_list))

        # 4. If we average all activities, is the three-hour window active?
        if len(activity_list) > 0:
            average_activity = sum(activity_list) / len(activity_list)
            if average_activity > criterion['threshold2']:
                return True
            else:
                return False
        else:
            # TODO: Discuss about this case - what if there is no data available?
            return True

    def __pad_walkdata(self, walkdata):
        padded_walkdata = [0] * 1440  # total number of minutes in a day
        for minute_data in walkdata:
            when = minute_data['when']
            steps = minute_data['steps']

            minute_index = when['hour'] * 24 + when['minute']
            padded_walkdata[minute_index] += steps
        return padded_walkdata


class LevelSequence(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True)
    order = models.IntegerField(null=True)
    is_used = models.BooleanField(default=False)
    when_created = models.DateTimeField(auto_now_add=True)
    when_used = models.DateTimeField(default=None, null=True)
    sequence_text = models.TextField(default="0,1,2,3,4,0,1,2,3,4")
    
    def create(cohort, order=None, sequence_text=None):
        query = LevelSequence.objects.filter(cohort=cohort)
        
        if query.exists():
            count = query.count()
        else:
            count = 0
        
        if sequence_text is None:
            return LevelSequence.objects.create(cohort=cohort,
                                            order=(order if order is not None else (count + 1)))
        else:
            return LevelSequence.objects.create(cohort=cohort,
                                            order=(order if order is not None else (count + 1)),
                                            sequence_text=sequence_text)

class LevelSequenceBlock(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True)
    seq_block = models.TextField(null=True, default=None)
    when_created = models.DateTimeField(auto_now_add=True)
    when_used = models.DateTimeField(null=True, default=None)

class LevelSequence_User(models.Model):
    user = models.OneToOneField(User, on_delete = models.DO_NOTHING)
    level_sequence = models.OneToOneField(LevelSequence, on_delete=models.DO_NOTHING)
    assigned = models.DateTimeField(auto_now_add=True)
