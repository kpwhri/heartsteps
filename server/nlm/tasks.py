from celery import shared_task

from nlm.models import StudyType, CohortAssignment
from nlm.services import StudyTypeService, LogService
import pprint

from generic_messages.services import GenericMessagesService
from participants.models import Participant


def log(msg):
    log_service = LogService(subject_name="nlm_task")
    log_service.log(value=msg, purpose="INFO")
    # print(msg)
    return log_service
                


@shared_task
def nlm_base_hourly_task(parameters):
    # try to bring all hourly studies
    hourly_study_types = StudyType.objects.filter(frequency=StudyType.HOURLY).all()
    
    for an_hourly_study_type in hourly_study_types:
        # try to bring nlm study architecture
        log("hourly study type discovered: {}".format(an_hourly_study_type.name))
        
        study_type_service = StudyTypeService.create_service(an_hourly_study_type)
        
        cohort_assignments = study_type_service.get_all_child_cohort_assignments()
        for a_cohort_assignment in cohort_assignments:
            log("cohort discovered: {}".format(a_cohort_assignment))
            
            a_cohort = a_cohort_assignment.cohort
            participants = Participant.objects.filter(cohort=a_cohort, active=True).all()
            
            for a_participant in participants:
                log("participant discovered: {}".format(a_participant))
                
                # generic_messages_service = GenericMessagesService.create_service(username=a_participant.user.username)
                # sent_message = generic_messages_service.send_message("test intervention", "Notification.GenericMessagesTest2", "Title from Tasks", "Body from Tasks: {}".format(parameters["minute"]), False)
                # log('Message sent using generic_messages: msg-{}, url- /notification/{}'.format("Sample Body: {}".format(parameters["minute"]), sent_message.data["messageId"]))
                
                study_type_service.handle_participant_hourly_task(a_participant.user)