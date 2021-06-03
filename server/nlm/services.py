from participants.models import Cohort, Participant
from django.db import models

from django.contrib.auth.models import User
from .models import StudyType, CohortAssignment, Conditionality, ConditionalityParameter
from .models import LogSubject, LogObject, LogPurpose, LogContents
from .models import PreloadedLevelSequenceFile, PreloadedLevelSequenceLine, PreloadedLevelSequenceLevel
from .models import LevelLineAssignment, LevelAssignment
from generic_messages.services import GenericMessagesService

class LogService:
    def __init__(self, subject_name='Unknown'):
        self.subject, created = LogSubject.objects.get_or_create(name=subject_name)
    
    def log(value="(Empty Message)", purpose="Unknown", object="Unknown"):
        log_service = LogService()
        log_service.log(value, purpose, object)
        
    def log(self, value="(Empty Message)", purpose="Unknown", object="Unknown"):
        log_object, created = LogObject.objects.get_or_create(name=object)
        log_purpose, created = LogPurpose.objects.get_or_create(name=purpose)
        
        LogContents.objects.create(
            subject=self.subject,
            object=log_object,
            purpose=log_purpose,
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
        query = LogContents.objects.filter(subject=self.subject)
        
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
            result = CohortAssignment.objects.create(cohort=cohort, studytype=study_type)
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
    def is_level_sequence_assigned(self, participant):
        return LevelLineAssignment.objects.filter(
            study_type=self.study_type,
            participant=participant
        ).exists()
    
    def assign_level_sequence(self, participant):
        return True
    
    def fetch_todays_level(self, participant):
        return StudyTypeService.LEVEL5
    
    def is_decision_needed(self, participant):
        return True
    
    def get_random_conditionality(self, participant):
        return True
    
    def get_need_conditionality(self, participant):
        return True
    
    def get_opportunity_condition(self, participant):
        return True
    
    def get_receptivity_condition(self, participant):
        return True
    
    def send_notification(self, participant):
        generic_messages_service = GenericMessagesService.create_service(username=participant.user.username)
        sent_message = generic_messages_service.send_message("test intervention", "Notification.GenericMessagesTest2", "Title from Tasks", "Body from Tasks", False)
        self.log_service.info('Message sent using generic_messages: /notification/{}'.format(sent_message.data["messageId"]))
        
        return True
    
    def handle_participant_hourly_task(self, participant):
        self.log_service.info("handling initiated", participant)
        
        # check if levels are assigned
        if self.is_level_sequence_assigned(participant):
            self.log_service.info("level sequence assignment checked", participant)
        else:
            level_sequence_id = self.assign_level_sequence(participant)
            self.log_service.info("new level sequence is assigned: {}".format(level_sequence_id), participant)
        
        # fetch level assignments
        todays_level = self.fetch_todays_level(participant)
        self.log_service.info("today's level is fetched: {}".format(todays_level), participant)
        self.log_service.data("todays_level:{}".format(todays_level), participant)
        
        # decide whether this participant should be decided or not
        is_decision_needed = self.is_decision_needed(participant)
        self.log_service.info("decision necessity is decided: {}".format(is_decision_needed), participant)
        self.log_service.data("is_decision_needed:{}".format(is_decision_needed), participant)
        
        if is_decision_needed:
            pass
        else:
            self.log_service.info("handling terminated because the decision is unnecessary.", participant)
            return False
        
        # per level, decide what to do
        if todays_level == StudyTypeService.LEVEL1:    # Recovery
            # for level 1 (recovery), we don't have to calculate the conditionalities.
            # decide whether to send bout planning window or not
            is_notification_needed = False
            self.log_service.info("since the participant is at level 1, no notification will be sent.", participant)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), participant)
            
            
        elif todays_level == StudyTypeService.LEVEL2:  # Random
            # for level 2 (random), we need to roll a dice
            
            # calculate conditionality 1
            random_conditionality = self.get_random_conditionality(participant)
            self.log_service.data("random_conditionality:{}".format(random_conditionality),participant)
            
            # decide whether to send bout planning window or not
            is_notification_needed = random_conditionality
            if is_notification_needed:
                self.log_service.info("since the participant is at level 2, by virtue of coin toss, notification will be sent.", participant)
            else:
                self.log_service.info("since the participant is at level 2, by virtue of coin toss, no notification will be sent.", participant)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), participant)
            
            
        elif todays_level == StudyTypeService.LEVEL3:  # N+O
            # for level 3 (N+O), we need two conditionalities
            
            # calculate conditionality 1
            need_conditionality = self.get_need_conditionality(participant)    
            self.log_service.data("need_conditionality:{}".format(need_conditionality), participant)
            
            # calculate conditionality 2
            opportunity_conditionality = self.get_opportunity_condition(participant)
            self.log_service.data("opportunity_conditionality:{}".format(opportunity_conditionality), participant)
                
            # decide whether to send bout planning window or not
            is_notification_needed = (need_conditionality and opportunity_conditionality)
            if is_notification_needed:
                self.log_service.info("since the participant is at level 3, by N+O conditionality, notification will be sent.", participant)
            else:
                self.log_service.info("since the participant is at level 3, by N+O conditionality, no notification will be sent.", participant)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), participant)
            
            
        elif todays_level == StudyTypeService.LEVEL4:  # N+R
            # for level 4 (N+R), we need two conditionalities
            # calculate conditionality 1
            need_conditionality = self.get_need_conditionality(participant)    
            self.log_service.data("need_conditionality:{}".format(need_conditionality), participant)
            
            # calculate conditionality 2
            receptivity_conditionality = self.get_receptivity_condition(participant)
            self.log_service.data("receptivity_conditionality:{}".format(receptivity_conditionality), participant)
                
            # decide whether to send bout planning window or not
            is_notification_needed = (need_conditionality and receptivity_conditionality)
            if is_notification_needed:
                self.log_service.info("since the participant is at level 4, by N+R conditionality, notification will be sent.", participant)
            else:
                self.log_service.info("since the participant is at level 4, by N+R conditionality, no notification will be sent.", participant)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), participant)
            
        elif todays_level == StudyTypeService.LEVEL5:  # N+R+O (Full)
            # for level 5 (N+R+O), we need three conditionalities
            # calculate conditionality 1
            need_conditionality = self.get_need_conditionality(participant)    
            self.log_service.data("need_conditionality:{}".format(need_conditionality), participant)
            
            # calculate conditionality 2
            receptivity_conditionality = self.get_receptivity_condition(participant)
            self.log_service.data("receptivity_conditionality:{}".format(receptivity_conditionality), participant)
            
            # calculate conditionality 3
            opportunity_conditionality = self.get_opportunity_condition(participant)
            self.log_service.data("opportunity_conditionality:{}".format(opportunity_conditionality), participant)
            
            # decide whether to send bout planning window or not
            is_notification_needed = (need_conditionality and receptivity_conditionality and opportunity_conditionality)
            if is_notification_needed:
                self.log_service.info("since the participant is at level 5, by N+R+O conditionality, notification will be sent.", participant)
            else:
                self.log_service.info("since the participant is at level 5, by N+R+O conditionality, no notification will be sent.", participant)
            self.log_service.data("is_notification_needed:{}".format(is_notification_needed), participant)

        else:
            self.log_service.error("unknown level is detected: {}".format(todays_level), participant)
            raise NotImplementedError
        
        # according to the decision, send the bout planning window or not
        if is_notification_needed:
            self.log_service.info("notification is being sent", participant)
            self.send_notification(participant)
        else:
            self.log_service.info("no notification will be sent", participant)
        
        self.log_service.info("handling terminated because the logic ended.", participant)
        
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