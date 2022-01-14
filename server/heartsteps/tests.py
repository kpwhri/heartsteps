from django.test import TestCase
from django.contrib.auth.models import User
from participants.models import Study, Cohort, Participant
from push_messages.models import Device
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from activity_summaries.models import ActivitySummary, Day
from datetime import date
from uuid import UUID
from django.db import transaction

class HeartStepsTestCase(TestCase):
    
    def printall(self, classname):
        """Print all db objects under the name

        Args:
            classname ([any]): Class name only
        """
        print("printing all {}s...".format(classname._meta.object_name))
        for obj in classname.objects.all():
            print(obj.__dict__)
        
        
        
    def setUp(self):
        self.user, _ = User.objects.get_or_create(username='user_for_test')
        
        study_name = "study_for_test"
        contact_name = "Debugger"
        contact_number = "8581234567"
        baseline_period = 7
        self.study, _ = Study.objects.get_or_create(
            name=study_name, 
            contact_name=contact_name,
            contact_number=contact_number,
            baseline_period=baseline_period
            )
        self.study.admins.add(self.user)
        self.study.save()
        
        cohort_name = "cohort_for_test"
        study_length = 365
        export_data = False   
        self.cohort, _ = Cohort.objects.get_or_create(
            study=self.study,
            name=cohort_name,
            study_length=study_length,
            export_data=export_data
            )
        
        self.participant, _ = Participant.objects.get_or_create(
            cohort=self.cohort, 
            user=self.user, 
            enrollment_token='test',
            heartsteps_id='test',
            study_start_date=date(2021, 9, 1)
            )
        
        self.device, _ = Device.objects.get_or_create(
            token="fake_device",
            user = self.user,
            active=True
        )
        
        self.user2 = User.objects.create(username="user2")
        self.participant2 = Participant.objects.create(user=self.user2, cohort=self.cohort, study_start_date=self.participant.study_start_date)
            

    def list_all(self, list_class, msg_index):
        for index, item in enumerate(list_class):
            print("[{}].tearDown[{}-{}]: {}".format(id(self), msg_index, index, list(map(lambda x: x.__dict__, item.objects.all()))))
            pass
            
    def tearDown(self):
        self.user.delete()
        self.user2.delete()
        ActivitySummary.objects.all().delete()
        self.study.delete()
        
    def checkif_non_none(self, obj_dict):
        for k, v in obj_dict.items():
            assert v is not None, ("{} is None".format(k))
    
    def checkif_has_attr(self, obj_name, obj, attrlist):
        for attr in attrlist:
            assert hasattr(obj, attr), "{} does not have '{}' attribute".format(obj_name, attr)
    
    def checkif_has_key(self, obj_name, obj, keylist):
        for key in keylist:
            assert key in obj, ("{} does not have '{}' key".format(obj_name, key))
            