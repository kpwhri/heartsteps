from celery import shared_task

from nlm.services import LogService

@shared_task
def hourly_task_test(minute):

    log_service = LogService(subject_name="hourly_task_test")
    
    log_service.log(value="minute:{}".format(minute))
    
    print(minute)