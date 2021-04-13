from participants.models import Cohort, Participant

from .models import CohortAssignment, ParticipantAssignment

class NLMService:
    class __DBSafeGuard:
        """Provide safe access to database. 
        """        
        
        def __init__(self, nlmservice):
            """Initiate DBSafeGuard toolbox
            
            Args:
                nlmservice (NLMService): parent nlmService

            Raises:
                ValueError: [description]
            """            
            if nlmservice:
                self.service = nlmservice
            else:
                raise ValueError("nlmservice parameter cannot be null.")
            
        def get_all_cohort_assignments_query(self):
            """Returns all cohort assignments as a query.
            
            ** This is a safeguard restricting direct access to the database. Please use this. **

            Args:
                user (django.contrib.auth.models.User): current user. it limits responsible studies.
            
            Returns:
                django.db.models.manager.BaseManager: query for the cohort assignments
            """        
            query = CohortAssignment.objects.filter(user=self.service.user)
            
            return query
        
        def create_new_cohort_assignment_to_NLM(self, cohort):
            """Create CohortAssignment DB object. 
            
            ** This is a safeguard restricting direct access to the database. Please use this. **

            Args:
                user (django.contrib.auth.models.User): current user. it limits responsible studies.
                cohort (participants.models.Cohort): target cohort to be applied

            Returns:
                QuerySet: all instances of the cohort assignment (nlm.models.CohortAssignment)
            """        
            result = CohortAssignment.objects.create(cohort=cohort, user=self.service.user)
            return result
        
        def get_cohort_assignment(self, cohort):
            """Returns cohort assignment

            Args:
                cohort (Cohort): target cohort for the cohort assignment

            Returns:
                CohortAssignment: CohortAssignment Object
            """
            nlm_assignment_query = CohortAssignment.objects.filter(user=self.service.user, cohort=cohort)
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
                result = ParticipantAssignment.objects.get_or_create(participant=participant, cohort=cohort)
                participant_assignment_list.append(result)
            
            return participant_assignment_list
            
        
    def __init__(self, user):
        """Initialize NLM Service instance
        
        Args:
            user (django.contrib.auth.models.User): current user. it limits responsible studies.

        Raises:
            ValueError: if user is None
        """        
        if user:
            self.user = user
        else:
            raise ValueError("user parameter is invalid")
        
        self.dsg = NLMService.__DBSafeGuard(self)
    
    def assign_cohort_to_nlm(self, cohort):
        """Assigns participants in a cohort into the NLM study.
        
        This will be generalized soon.

        Args:
            cohort (participants.models.Cohort): target cohort to be applied

        Returns:
            QuerySet: all instances of the cohort assignment (nlm.models.CohortAssignment)
        """       
        if cohort: 
            if isinstance(cohort, Cohort):
                nlm_assignment_query = self.dsg.get_cohort_assignment(cohort)
                if nlm_assignment_query and nlm_assignment_query.count() > 0:
                    result = nlm_assignment_query.all() 
                    self.apply_all_cohort_assignments()
                    return result
                else:
                    result = self.dsg.create_new_cohort_assignment_to_NLM(cohort)
                    self.apply_all_cohort_assignments()
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
        else:
            raise Exception("No cohort assignment to apply")
                
            
    