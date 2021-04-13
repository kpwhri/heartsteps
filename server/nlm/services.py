from participants.models import Cohort

from .models import CohortAssignment

class NLMService:
    def __init__(self, user):
        if user:
            self.user = user
        else:
            raise ValueError("user parameter is invalid")
    
    def __get_all_cohort_assignments_query(self):
        query = CohortAssignment.objects
        return query
    
    def assign_cohort_to_nlm(self, cohort):
        nlm_assignment_query = CohortAssignment.objects.filter(cohort=cohort)
        if nlm_assignment_query and nlm_assignment_query.count > 0:
            result = nlm_assignment_query.all() 
            self.apply_all_cohort_assignments()
            return result
        else:
            result = CohortAssignment.objects.create(cohort=cohort)
            self.apply_all_cohort_assignments()
            return result
    
    def apply_all_cohort_assignments(self):
        cohort_assignment_query = self.__get_all_cohort_assignments_query()
        if cohort_assignment_query:
            for cohort_assignment in cohort_assignment_query.all():
                self.apply_cohort_assignment(cohort_assignment)
    
    def apply_cohort_assignment(self, cohort):
        pass
                