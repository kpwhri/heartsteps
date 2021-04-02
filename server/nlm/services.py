from participants.models import Cohort

from .models import CohortAssignment

class NLMService:
    def __init__(self, user):
        self.user = user
    
    def assign_cohort_to_nlm(self, cohort):
        nlm_assignment_query = CohortAssignment.objects.filter(cohort=cohort)
        if nlm_assignment_query and nlm_assignment_query.count > 0:
            return nlm_assignment_query.all() 
        else:
            result = CohortAssignment.objects.create(cohort=cohort)
            return result