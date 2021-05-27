from celery import shared_task

from nlm.models import StudyType, CohortAssignment
from nlm.services import StudyTypeService, LogService
import pprint

from participants.models import Participant


def log(depth, msg):
    log_service = LogService(subject_name="nlm_task")
    msg = " ".ljust(depth) + msg
    log_service.log(value=msg)
    print(msg)
    return log_service
                


@shared_task
def nlm_base_hourly_task(parameters):
    log(0, "parameter:{}".format(pprint.pformat(parameters)))
    
    # try to bring all hourly studies
    hourly_study_types = StudyType.objects.filter(frequency=StudyType.HOURLY).all()
    
    for an_hourly_study_type in hourly_study_types:
        # try to bring nlm study architecture
        log(1, "hourly study type discovered: {}".format(an_hourly_study_type.name))
        
        study_type_service = StudyTypeService.create_service(an_hourly_study_type)
        
        cohort_assignments = study_type_service.get_all_child_cohort_assignments()
        for a_cohort_assignment in cohort_assignments:
            log(2, "cohort discovered: {}".format(a_cohort_assignment))
            
            a_cohort = a_cohort_assignment.cohort
            participants = Participant.objects.filter(cohort=a_cohort, active=True).all()
            
            for a_participant in participants:
                log(3, "participant discovered: {}".format(a_participant))
                
                
