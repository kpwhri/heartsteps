from heartsteps.tests import HeartStepsTestCase
from nlm.services import StudyTypeService, LogService

class StudyTypeServiceTest(HeartStepsTestCase):
    def test_log(self):
        log_service = LogService(subject_name="nlm.test")
        
        import time
        
        log_service.log()
        time.sleep(0.500)
        log_service.log()

    def test_dump_all_logging(self):
        log_service = LogService(subject_name="nlm.test")
        
        log_service.dump()
        
    def test_clear_all_logging(self):
        log_service = LogService(subject_name="nlm.test")
        
        import time
        
        log_service.clear()        
        log_service.log()
        time.sleep(0.200)
        log_service.log()
        
        log_service.clear()  
