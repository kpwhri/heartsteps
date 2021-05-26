from participants.models import Cohort, Participant

from django.contrib.auth.models import User
from .models import StudyType, CohortAssignment, ParticipantAssignment, Conditionality, LogSubject, LogObject, LogPurpose, LogContents, ConditionalityParameter


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
        query = LogContents.objects.filter().order_by("-logtime")
        
        log_list = []
        
        if query:
            for item in query.all():
                log_list.append({
                    'logtime': item.logtime,
                    'subject': item.subject.name,
                    'object': item.object.name,
                    'purpose': item.purpose.name,
                    'value': item.value
                })
        
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

    def clear(self):
        """Do Not User This Method. This is only for development.
        This will be removed when the development is finished.
        """
        query = LogContents.objects.filter(subject=self.subject)
        query.delete()

            
        
class StudyTypeService:
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
            study_type_object, created = StudyType.objects.get_or_create(name=study_type_name)
            study_type_object.admins.set([self.user])
            
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
        
        def get_or_create_participant_assignment_list(self, cohort_assignment):
            """Return a list of participant assignments under a cohort assignment

            Args:
                cohort_assignment (CohortAssignment): target cohort assignment for the participant assignment list

            Returns:
                List: Participant Assignment List
            """
            cohort = cohort_assignment.cohort
            
            participant_query = Participant.objects.filter(cohort=cohort)
            
            participant_assignment_list = []
            for participant in participant_query.all():
                result = ParticipantAssignment.objects.get_or_create(participant=participant, cohort_assignment=cohort_assignment)
                participant_assignment_list.append(result[0])
            
            return participant_assignment_list
        
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
            
            
    
    def __init__(self, user, study_type_name):
        if user:
            self.user = user
        else:
            raise ValueError("user parameter is invalid")
        
        self.dsg = StudyTypeService.__DBSafeGuard(self.user)
        
        self.study_type, new_study_type = self.dsg.get_or_create_study_type(study_type_name)
    
    def assign_cohort(self, cohort):
        """Assigns participants in a cohort into the particular study type.
        
        Args:
            cohort (participants.models.Cohort): target cohort to be applied

        Returns:
            QuerySet: all instances of the cohort assignment (nlm.models.CohortAssignment)
        """       
        if cohort: 
            if isinstance(cohort, Cohort):
                self.dsg.create_new_cohort_assignment(cohort, self.study_type)
                result = self.apply_all_cohort_assignments()
                return result
            else:
                raise ValueError("passed parameter is not Cohort:{}".format(cohort))
        else:
            raise ValueError("cohort parameter is {}".format(cohort))
        
    
    def apply_all_cohort_assignments(self):
        """Fetch all non-NLM participants in all NLM-assigned cohorts, put them into a NLM Participant assignment
        
        This will be generalized soon.
        """        
        
        cohort_assignment_query = self.dsg.get_all_cohort_assignments_query()
        if cohort_assignment_query:
            all_participant_assignment_list = []
            for cohort_assignment in cohort_assignment_query.all():
                participant_assignment_list = self.dsg.get_or_create_participant_assignment_list(cohort_assignment)
                all_participant_assignment_list = all_participant_assignment_list + participant_assignment_list
            return all_participant_assignment_list
        
                
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
    
    def get_nlm_participants_dict(self):
        """Returns a list of assigned participant dictionaries in NLM type study
        """
        
        participant_assignment_list = self.apply_all_cohort_assignments()
        
        participant_list = []
        
        if participant_assignment_list:
            for participant_assignment in participant_assignment_list:
                participant_list.append(participant_assignment.participant)
            
        return participant_list
    
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
    
