# base imports
from datetime import datetime, timedelta
import pytz
import random

# django imports
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# other app imports
from participants.models import Cohort, Participant
from generic_messages.services import GenericMessagesService
from daily_step_goals.services import StepGoalsService
from activity_summaries.models import Day
from days.services import DayService

# same app imports
from .models import StudyType, CohortAssignment, Conditionality, ConditionalityParameter
from .models import LogContents
from .models import PreloadedLevelSequenceFile, PreloadedLevelSequenceLine, PreloadedLevelSequenceLevel
from .models import LevelLineAssignment, LevelAssignment
from .models import Preference




class LogService:
    def __init__(self, subject_name=None):
        self.subject_str = subject_name
    
    def log(value=None, purpose=None, object=None):
        log_service = LogService()
        log_service.log(value, purpose, object)
        
    def log(self, value=None, purpose=None, object=None):
        LogContents.objects.create(
            subject_str=self.subject_str,
            object_str=object,
            purpose_str=purpose,
            value=value
        )
    
    def dump(pretty=False):
        query = LogContents.objects.filter().order_by("-logtime")[:100]
        
        log_list = []
        
        if query:
            for item in query.all():
                log_list.append(str(item))
        
        if pretty:
            import json

            from django.core.serializers.json import DjangoJSONEncoder

            return json.dumps(
                log_list,
                sort_keys=True,
                indent=2,
                cls=DjangoJSONEncoder
            )
        else:
            return log_list

    def clear_all():
        """Do Not User This Method. This is only for development.
        This will be removed when the development is finished.
        """
        LogContents.objects.all().delete()
        
    def clear(self):
        """Do Not User This Method. This is only for development.
        This will be removed when the development is finished.
        """
        query = LogContents.objects.filter(subject_str=self.subject_str)
        
        query.delete()

    def __get_object_str(self, obj:models.Model):
        if isinstance(obj, Participant):
            return "{}:{}".format(obj.__class__.__name__, obj.heartsteps_id)
        else:
            return "{}:{}".format(obj.__class__.__name__, obj.id)
            
    def info(self, msg, obj:models.Model):
        self.log(value=msg, purpose="INFO", object=self.__get_object_str(obj))
    
    def data(self, msg, obj:models.Model):
        self.log(value=msg, purpose="DATA", object=self.__get_object_str(obj))
    
    def error(self, msg, obj:models.Model):
        self.log(value=msg, purpose="ERROR", object=self.__get_object_str(obj))
        
class StudyTypeService:
    
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3
    LEVEL4 = 4
    LEVEL5 = 5
    
    LEVEL_DEFAULT = LEVEL5  # full JITAI is default.
    
    class __DBSafeGuard:
        """Provide safe access to database. 
        """        
        
        def __init__(self, user):
            """Initiate DBSafeGuard toolbox
            
            Args:
                user (User): subject user

            Raises:
                ValueError: [description]
            """            
            if user:
                self.user = user
            else:
                raise ValueError("user parameter cannot be null.")
       
        def get_or_create_study_type(self, study_type_name):
            """Returns StudyType with a name. If not exists, it creates an object for it.

            Args:
                study_type_name (str): study type name

            Returns:
                tuple : a Tuple of (object, created)
            """
            study_type_object, created = StudyType.objects.get_or_create(name=study_type_name, frequency=StudyType.HOURLY)
            study_type_object.admins.add(self.user)
            study_type_object.save()
            
            return (study_type_object, created)
            
        def get_all_cohort_assignments_query(self):
            """Returns all cohort assignments as a query.
            
            ** This is a safeguard restricting direct access to the database. Please use this. **

            Args:
                user (django.contrib.auth.models.User): current user. it limits responsible studies.
            
            Returns:
                django.db.models.manager.BaseManager: query for the cohort assignments
            """        
            query = CohortAssignment.objects.filter(cohort__study__admins=self.user)
            
            return query
        
        def create_new_cohort_assignment(self, cohort, study_type):
            """Create CohortAssignment DB object. 
            
            ** This is a safeguard restricting direct access to the database. Please use this. **

            Args:
                user (django.contrib.auth.models.User): current user. it limits responsible studies.
                cohort (participants.models.Cohort): target cohort to be applied
                study_type (nlm.models.StudyType): target study cohort to be applied

            Returns:
                QuerySet: all instances of the cohort assignment (nlm.models.CohortAssignment)
            """        
            result, _ = CohortAssignment.objects.get_or_create(cohort=cohort, studytype=study_type)
            return result
        
        def get_cohort_assignment(self, cohort):
            """Returns cohort assignment

            Args:
                cohort (Cohort): target cohort for the cohort assignment

            Returns:
                CohortAssignment: CohortAssignment Object
            """
            nlm_assignment_query = CohortAssignment.objects.filter(cohort=cohort)
            return nlm_assignment_query
        
        def create_conditionality(self, name, description, study_type, module_path):
            """create a new conditionality

            Args:
                name (str): conditionality name (unique)
                description (str): conditionality description
                study_type (StudyType): the StudyType that the conditionality is in
                module_path (str): conditionality module (unique)

            Returns:
                Conditionality: newly created conditionality object
            """
            return Conditionality.objects.create(name=name, description=description, studytype=study_type, module_path=module_path)
        
        def delete_conditionality(self, module_path):
            return Conditionality.objects.filter(studytype__admins=self.user, module_path=module_path).delete()
        
        def clear_all_conditionalities(self):
            """
            Do not use this other than development purporse
            """
            return Conditionality.objects.filter(studytype__admins=self.user).delete()  
        
        def set_conditionality_parameter(self, conditionality, parameter_fullname, value):
            import datetime
            from django.conf import settings
            from django.utils.timezone import make_aware

            naive_datetime = datetime.datetime.now()
            aware_datetime = make_aware(naive_datetime)
            
            from datetime import datetime
            old_parameter = ConditionalityParameter.objects.filter(conditionality=conditionality, 
                                                                   parameter_fullname=parameter_fullname, 
                                                                   period_begin__lte=aware_datetime,
                                                                   period_finish__gte=aware_datetime).order_by('-period_begin').first()
            
            if old_parameter:
                old_parameter.period_finish = aware_datetime
                            
            return ConditionalityParameter.objects.create(
                conditionality=conditionality,
                period_begin=aware_datetime,
                parameter_fullname=parameter_fullname,
                value=value,
                value_type = type(value)
            )
        
        def get_all_conditionality_parameters(self):
            return ConditionalityParameter.objects.all()
        
        def remove_conditionality(self, conditionality, parameter_fullname):
            return ConditionalityParameter.objects.filter(
                conditionality=conditionality, 
                parameter_fullname=parameter_fullname).delete()

        def get_conditionality_parameters(self, conditionality):
            return ConditionalityParameter.objects.filter(
                conditionality=conditionality
            ).all()
            
            
    
    def __init__(self, study_type_name, user=None, frequency=StudyType.HOURLY):
        assert study_type_name, "Study type name cannot be None"
        self.log_service = LogService(subject_name="StudyTypeService")
        if user:
            self.isreadonly = False
            self.user = user
            
            self.dsg = StudyTypeService.__DBSafeGuard(self.user)
        
            self.study_type, created = StudyType.objects.get_or_create(name=study_type_name, frequency=frequency)
            self.study_type.admins.add(self.user)
        else:
            self.user = None
            self.isreadonly = True
            if StudyType.objects.filter(name=study_type_name).exists():
                self.study_type = StudyType.objects.get(name=study_type_name, active=True)
                self.user = None
            else:
                raise StudyType.DoesNotExist
    
    def create_service(study_type):
        return StudyTypeService(study_type.name, frequency=study_type.frequency)
    
    def get_all_child_cohort_assignments(self):
        query = CohortAssignment.objects.filter(studytype=self.study_type, active=True)
        
        return query.all()
    
    
    # TODO: fill up with real logics
    def is_level_sequence_assigned(self, user):
        return LevelLineAssignment.objects.filter(
            study_type=self.study_type,
            user=user
        ).exists()
    
    def localize_datetime(self, user, datetime_in_UTC):
        day_service = DayService(user)
        local_timezone = day_service.get_timezone_at(datetime_in_UTC)
        if isinstance(datetime_in_UTC, datetime):
            return datetime_in_UTC.astimezone(local_timezone)
        else:
            return datetime(datetime_in_UTC.year, datetime_in_UTC.month, datetime_in_UTC.day, tzinfo=local_timezone)
    
    def assign_level_sequence(self, user, file_nickname):
        # check parameters
        assert file_nickname is not None, "File nickname is required"
        
        # bring the sequence file (nickname is a unique attribute)
        try:
            sequence_file = PreloadedLevelSequenceFile.objects.get(
                nickname=file_nickname,
                user__in=self.study_type.admins.all(),
            )    
        except PreloadedLevelSequenceFile.DoesNotExist:
            raise PreloadedLevelSequenceFile.DoesNotExist("No preloaded sequence file is found.")
        
        # under the file, look up next available sequence line
        try:    
            next_available_sequence = PreloadedLevelSequenceLine.objects.filter(
                sequence_file=sequence_file,
                is_used=False
            ).order_by("sequence_serial_number").first()
        except PreloadedLevelSequenceLine.DoesNotExist:
            raise Exception("No unused line is found.")
            
        # try to use user's study_start_date
        # if the study_start_date is not available, use today
        # TODO: change to "actual" start date
        participant = Participant.objects.get(user=user)
        if participant.study_start_date:
            study_start_date = self.localize_datetime(user, participant.study_start_date).date()
        else:
            study_start_date = self.localize_datetime(user, timezone.now()).date()
        
        # record the assignment
        line_assignment = LevelLineAssignment.objects.create(
            study_type=self.study_type,
            user=user,
            preloaded_sequence_line=next_available_sequence
        )
        
        preloaded_levels = PreloadedLevelSequenceLevel.objects.filter(sequence_line=next_available_sequence).order_by("day_serial_number").all()
        
        for a_preloaded_level in preloaded_levels:
            the_day = study_start_date + timedelta(days=a_preloaded_level.day_serial_number)
            LevelAssignment.objects.create(
                line_assignment=line_assignment,
                user=user,
                date=the_day,
                level=a_preloaded_level.level
            )
            
        return next_available_sequence
    
    def fetch_todays_level(self, user):
        today_date = self.localize_datetime(user, timezone.now()).date()
        
        try:
            todays_level = LevelAssignment.objects.get(user=user, date=today_date)
            return todays_level.level
        except LevelAssignment.DoesNotExist:
            self.log_service.info("No LevelAssignment is found. Using default Level: {}".format(StudyTypeService.LEVEL_DEFAULT), user)
            return StudyTypeService.LEVEL_DEFAULT
        
        
    
    def is_decision_needed(self, user, test_time=None):
        # fetch the user's decision window preferences
        first_decision_point_hour = self.get_first_decision_point_hour(user)
        
        # get decision point expiration window (in minutes)
        decision_point_expiration_window = self.get_decision_point_expiration_window()
        
        # get decision point gap (in hours)
        decision_point_gap = self.get_decision_point_gap()
        
        # decide if now is the user's decision point or not
        if test_time:
            current_time = test_time
        else:
            current_time = self.localize_datetime(user, timezone.now())
        
        decision_points = self.construct_decision_points(first_decision_point_hour, decision_point_gap, current_time)
        
        # intentionally iterates twice. Later, we might get the index of which decision point we are near to.
        for i in range(0, 4):
            if current_time >= decision_points[i] and current_time - decision_points[i] <= timedelta(minutes=decision_point_expiration_window):
                return True
        
        return False

    def construct_decision_points(self, first_decision_point_hour, decision_point_gap, current_time):
        decision_points = []
        temp_time = current_time
        temp_time = temp_time.replace(
            hour=first_decision_point_hour, 
            minute=0,
            second=0,
            microsecond=0)
        decision_points.append(temp_time)
        
        for i in range(1, 4):
            temp_time = temp_time.replace(hour=((temp_time.hour + decision_point_gap) % 24))
            decision_points.append(temp_time)
        return decision_points

    def get_decision_point_gap(self):
        decision_point_gap, _ = Preference.try_to_get(
            path="nlm.bout_planning.decision_point_gap",
            default=3, 
            convert_to_int=True)
            
        return decision_point_gap

    def get_decision_point_expiration_window(self):
        decision_point_expiration_window, _ = Preference.try_to_get(
            path="nlm.bout_planning.decision_point_expiration_window",
            default=10, 
            convert_to_int=True)
            
        return decision_point_expiration_window

    def get_first_decision_point_hour(self, user):
        first_decision_point_hour, _ = Preference.try_to_get(
            path="nlm.bout_planning.first_decision_point_hour", 
            user=user, 
            default=8, 
            convert_to_int=True)
            
        return first_decision_point_hour
            
    def get_random_conditionality(self, user, test_value=None):
        # with a random criterion (0~100). if the random value equals to or less than the criteria, the conditionality is "True"
        random_criteria, fromdb = Preference.try_to_get("nlm.bout_planning.conditionality.random.random_criteria", default=50, convert_to_int=True)
        
        if test_value is None:
            random_value = random.random() * 100
        else:
            random_value = test_value
        
        return random_value <= random_criteria
    
    def get_last_day_achieved(self, user):
        last_day_date = (datetime.now() - timedelta(days=1)).date()
        last_day_step_goal = self.get_step_goal(
            user, 
            date=last_day_date)
        
        last_day_step_count = self.get_steps(user, last_day_date)
        
        return (last_day_step_goal < last_day_step_count)
    
    def get_steps(self, user, date=None):
        if date is None:
            date = datetime.now().astimezone(pytz.utc).date()
        day_query = Day.get_all_days_query(user, date)
        if day_query.count() > 0:
            return_row = day_query.last()
            return return_row.steps
        else:
            day = Day.objects.create(
                user = user,
                date = date
            )
            day.update_from_activities()
            day.update_from_fitbit()
        return day.steps
    
    def get_today_steps(self, user):
        return self.get_steps(user)
    
    def get_need_conditionality(self, user):
        today_step_goal = self.get_step_goal(user)
        
        today_steps = self.get_today_steps(user)
        last_day_achieved = self.get_last_day_achieved(user)
        
        first_decision_point_hour = self.get_first_decision_point_hour(user)
        decision_point_gap = self.get_decision_point_gap(user)
        current_time = self.localize_datetime(user, datetime.now().astimezone(pytz.UTC))
        
        decision_points = self.construct_decision_points(
            first_decision_point_hour, decision_point_gap, current_time
        )
        decision_point_interval_index = self.get_decision_point_interval_index(current_time, decision_points)
        
        
        if decision_point_interval_index <= 0:
            return not last_day_achieved
        elif 0 < decision_point_interval_index and decision_point_interval_index <=4:
            prorated_goal = today_step_goal * decision_point_interval_index / 4 
            
            return prorated_goal > today_steps

    def get_step_goal(self, user, date=None):
        step_goals_service = StepGoalsService(user)
        step_goal = step_goals_service.get_step_goal(date)
        return step_goal
        
    def get_decision_point_interval_index(self, current_time, decision_points):
        twelveth_hour = decision_points[0].replace(hour=((decision_points[0].hour+12) % 24))
        
        if current_time < decision_points[0]:
            decision_point_interval_index = -1
        elif current_time < decision_points[1]:
            decision_point_interval_index = 0
        elif current_time < decision_points[2]:
            decision_point_interval_index = 1
        elif current_time < decision_points[3]:
            decision_point_interval_index = 2
        elif current_time < twelveth_hour:
            decision_point_interval_index = 3
        else:
            decision_point_interval_index = 4
            
            
        return decision_point_interval_index
        
        
        
    
    def get_opportunity_condition(self, user):
        return True
    
    def get_receptivity_condition(self, user):
        return True
    
    def send_notification(self, user):
        generic_messages_service = GenericMessagesService.create_service(username=user.username)
        sent_message = generic_messages_service.send_message("test intervention", "Notification.GenericMessagesTest2", "Title from Tasks", "Body from Tasks", False)
        self.log_service.info('Message sent using generic_messages: /notification/{}'.format(sent_message.data["messageId"]))
        
        return True
    
    def handle_user_hourly_task(self, user):
        self.log_service.info("handling initiated", user)
        
        # check if levels are assigned
        if self.is_level_sequence_assigned(user):
            self.log_service.info("level sequence assignment checked", user)
        else:
            level_sequence_id = self.assign_level_sequence(user, "NLM sequence")
            self.log_service.info("new level sequence is assigned: {}".format(level_sequence_id), user)
        
        # fetch level assignments
        todays_level = self.fetch_todays_level(user)
        self.log_service.info("today's level is fetched: {}".format(todays_level), user)
        self.log_service.data("todays_level:{}".format(todays_level), user)
        
        # decide whether this user should be decided or not
        is_decision_needed = self.is_decision_needed(user)
        self.log_service.info("decision necessity is decided: {}".format(is_decision_needed), user)
        self.log_service.data("is_decision_needed:{}".format(is_decision_needed), user)
        
        if is_decision_needed:
            pass
        else:
            self.log_service.info("handling terminated because the decision is unnecessary.", user)
            return False
        
        # per level, decide what to do
        if todays_level == StudyTypeService.LEVEL1:    # Recovery
            # for level 1 (recovery), we don't have to calculate the conditionalities.
            # decide whether to send bout planning window or not
            is_notification_needed = False
            self.log_service.info("since the user is at level 1, no notification will be sent.", user)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), user)
            
            
        elif todays_level == StudyTypeService.LEVEL2:  # Random
            # for level 2 (random), we need to roll a dice
            
            # calculate conditionality 1
            random_conditionality = self.get_random_conditionality(user)
            self.log_service.data("random_conditionality:{}".format(random_conditionality),user)
            
            # decide whether to send bout planning window or not
            is_notification_needed = random_conditionality
            if is_notification_needed:
                self.log_service.info("since the user is at level 2, by virtue of coin toss, notification will be sent.", user)
            else:
                self.log_service.info("since the user is at level 2, by virtue of coin toss, no notification will be sent.", user)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), user)
            
            
        elif todays_level == StudyTypeService.LEVEL3:  # N+O
            # for level 3 (N+O), we need two conditionalities
            
            # calculate conditionality 1
            need_conditionality = self.get_need_conditionality(user)    
            self.log_service.data("need_conditionality:{}".format(need_conditionality), user)
            
            # calculate conditionality 2
            opportunity_conditionality = self.get_opportunity_condition(user)
            self.log_service.data("opportunity_conditionality:{}".format(opportunity_conditionality), user)
                
            # decide whether to send bout planning window or not
            is_notification_needed = (need_conditionality and opportunity_conditionality)
            if is_notification_needed:
                self.log_service.info("since the user is at level 3, by N+O conditionality, notification will be sent.", user)
            else:
                self.log_service.info("since the user is at level 3, by N+O conditionality, no notification will be sent.", user)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), user)
            
            
        elif todays_level == StudyTypeService.LEVEL4:  # N+R
            # for level 4 (N+R), we need two conditionalities
            # calculate conditionality 1
            need_conditionality = self.get_need_conditionality(user)    
            self.log_service.data("need_conditionality:{}".format(need_conditionality), user)
            
            # calculate conditionality 2
            receptivity_conditionality = self.get_receptivity_condition(user)
            self.log_service.data("receptivity_conditionality:{}".format(receptivity_conditionality), user)
                
            # decide whether to send bout planning window or not
            is_notification_needed = (need_conditionality and receptivity_conditionality)
            if is_notification_needed:
                self.log_service.info("since the user is at level 4, by N+R conditionality, notification will be sent.", user)
            else:
                self.log_service.info("since the user is at level 4, by N+R conditionality, no notification will be sent.", user)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), user)
            
        elif todays_level == StudyTypeService.LEVEL5:  # N+R+O (Full)
            # for level 5 (N+R+O), we need three conditionalities
            # calculate conditionality 1
            need_conditionality = self.get_need_conditionality(user)    
            self.log_service.data("need_conditionality:{}".format(need_conditionality), user)
            
            # calculate conditionality 2
            receptivity_conditionality = self.get_receptivity_condition(user)
            self.log_service.data("receptivity_conditionality:{}".format(receptivity_conditionality), user)
            
            # calculate conditionality 3
            opportunity_conditionality = self.get_opportunity_condition(user)
            self.log_service.data("opportunity_conditionality:{}".format(opportunity_conditionality), user)
            
            # decide whether to send bout planning window or not
            is_notification_needed = (need_conditionality and receptivity_conditionality and opportunity_conditionality)
            if is_notification_needed:
                self.log_service.info("since the user is at level 5, by N+R+O conditionality, notification will be sent.", user)
            else:
                self.log_service.info("since the user is at level 5, by N+R+O conditionality, no notification will be sent.", user)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), user)

        else:
            self.log_service.error("unknown level is detected: {}".format(todays_level), user)
            raise NotImplementedError
        
        # according to the decision, send the bout planning window or not
        if is_notification_needed:
            self.log_service.info("notification is being sent", user)
            self.send_notification(user)
        else:
            self.log_service.info("no notification will be sent", user)
        
        self.log_service.info("handling terminated because the logic ended.", user)
        
        return True
    
    def assign_cohort(self, cohort):
        """Assigns participants in a cohort into the particular study type.
        
        Args:
            cohort (participants.models.Cohort): target cohort to be applied

        Returns:
            QuerySet: all instances of the cohort assignment (nlm.models.CohortAssignment)
        """       
        if cohort: 
            if isinstance(cohort, Cohort):
                return self.dsg.create_new_cohort_assignment(cohort, self.study_type)
            else:
                raise ValueError("passed parameter is not Cohort:{}".format(cohort))
        else:
            raise ValueError("cohort parameter is {}".format(cohort))
        
        
                
    def get_nlm_cohorts_dict(self):
        """
        Returns a list of cohort dictionaries
        """
        cohort_assignment_query = self.dsg.get_all_cohort_assignments_query()
        
        if cohort_assignment_query:
            cohort_list = []
            for cohort_assignment in cohort_assignment_query.all():
                cohort = cohort_assignment.cohort
                cohort_list.append({'name': cohort.name})
            return cohort_list
        else:
            return []
    
    def add_conditionality(self, name, description, module_path):
        """Adds a new conditionality
        Returns: 
            Conditionality: the new conditionality (nlm.models.Conditionality)
        """
        return self.dsg.create_conditionality(name, description, self.study_type, module_path)
        
    def remove_conditionality(self, module_path):
        """Removes a conditionality"""
        return self.dsg.delete_conditionality(module_path)
        
    def call_conditionality(self, module, parameters=None):
        """Run a conditionality by a module path

        Args:
            module (str): modulepath
        """
        
        params = module.split(".")
        functionname = params[-1]
        modulename = ".".join(params[0:-1])
        
        import importlib
        moduleobj = importlib.import_module(name=modulename)
        return getattr(moduleobj, functionname)(parameters)
    
    def set_conditionality_parameter(self, conditionality, parameter_fullname, value):
        return self.dsg.set_conditionality_parameter(conditionality, parameter_fullname, value)
    
    def remove_conditionality_parameter(self, conditionality, parameter_fullname):
        return self.dsg.remove_conditionality(conditionality, parameter_fullname)
    
    def get_conditionality_parameters(self, conditionality):
        return self.dsg.get_conditionality_parameters(conditionality)
    
    def upload_level_csv(self, filename, nickname, lines):
        return PreloadedLevelSequenceFile.insert(self.user, filename, nickname, lines)
    
    def delete_level_csv(self, nickname):
        PreloadedLevelSequenceFile.objects.filter(user=self.user, nickname=nickname).all().delete()
        
    def is_cohort_assigned(self, cohort):
        return CohortAssignment.objects.filter(studytype=self.study_type, cohort=cohort).exists()