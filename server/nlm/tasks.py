from celery import shared_task

from nlm.models import StudyType
from nlm.services import StudyTypeService, LogService
import pprint
    
@shared_task
def nlm_base_hourly_task(parameters):
    log_service = LogService(subject_name="nlm_task")
    log_service.log(value="parameter:{}".format(pprint.pformat(parameters)))
    
    print("parameter:{}".format(pprint.pformat(parameters)))
    
    # try to bring all hourly studies
    hourly_study_types = StudyType.get_all(frequency="hourly")
    
    for an_hourly_study_type in hourly_study_types:
        # try to bring nlm study architecture
        log_service.log(value="  hourly study type discovered: {}".format(an_hourly_study_type.name))
        print("  hourly study type discovered: {}".format(an_hourly_study_type.name))
        
        cohorts = an_hourly_study_type.get_all_child_cohorts()
        for a_cohort in cohorts:
            log_service.log(value="    cohort discovered: {}".format(a_cohort))
            print("    cohort discovered: {}".format(a_cohort))
            