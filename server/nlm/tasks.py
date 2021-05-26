from celery import shared_task

from nlm.services import LogService

@shared_task
def nlm_base_hourly_task(parameters):
    import pprint
    
    log_service = LogService(subject_name="nlm_task")
    
    log_service.log(value="parameter:{}".format(pprint.pformat(parameters)))
    
    print("parameter:{}".format(pprint.pformat(parameters)))