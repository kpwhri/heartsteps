import requests
# from push_messages.clients import OneSignalClient
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from participants.models import Study, Cohort

import random
import datetime

class DevSendNotificationService:    
    def __init__(self, configuration=None):
        pass

    def send_dev_notification(self, device_id):
        self.send_notification(device_id)

    def get_one_signal_notification_url(self):
        return 'https://onesignal.com/api/v1/notifications'

    def get_api_key(self):
        if not hasattr(settings, 'ONESIGNAL_API_KEY'):
            raise ImproperlyConfigured('No OneSignal API KEY')
        return settings.ONESIGNAL_API_KEY
        
    def get_app_id(self):
        if not hasattr(settings, 'ONESIGNAL_APP_ID'):
            raise ImproperlyConfigured('No OneSignal APP ID')
        return settings.ONESIGNAL_APP_ID
    
    def __send(self, device_id, body=None, title=None, collapse_subject=None, data=None):
        response = requests.post(
            self.get_one_signal_notification_url(),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % (self.get_api_key())
            },
            json = {
                'app_id': self.get_app_id(),
                'include_player_ids': device_id,
                'contents': {
                    'en': body
                },
                'headings': {
                    'en': title
                },
                'collapse_id': collapse_subject,
                'data': data
            }
        )

        if response.status_code == 200:
            response_data = response.json()
            if 'errors' in response_data and response_data['errors'] and len(response_data['errors']) > 0:
                raise Exception(response_data['errors'[0]])
            message_id = response_data['id']
            return message_id
        else:
            raise Exception(response.text)
            
    def send_notification(self, device_id):
        message_response_id = self.__send(device_id = device_id,
                body = "test body",
                title = "test title",
                collapse_subject = "test collapse_subject",
                data = {}
            )
        
        return message_response_id


class DevStudyService:
    def __init__(self, user, configuration=None):
        self.user = user
    
    def getRandomName(self, heading, digits):
        formatstr = '%0{}X'.format(digits)
        randhex = formatstr % random.randrange(16**digits)
        return "{} {}".format(heading, randhex)
        
    def create_debug_study(self):
        study_name = self.getRandomName("Debug Study", 10)
        contact_name = "Debugger"
        contact_number = "8581234567"
        baseline_period = 7
        
        study_instance = Study.objects.create(name=study_name, 
                                            contact_name=contact_name,
                                            contact_number=contact_number,
                                            baseline_period=baseline_period                                            
                                            )
        study_instance.admins.set([self.user])
        
    def clear_debug_study(self):
        results = Study.objects.filter(contact_name__startswith="Debugger").delete()
        
        return "All debug Studies are deleted: {}".format(results)
    
    def get_all_debug_studies(self):
        results = Study.objects.filter(contact_name__startswith="Debugger")
        
        return results
    
    def create_debug_cohort(self, study):
        name = self.getRandomName("Debug Cohort", 10)
        study_length = 365
        export_data = False
        
        cohort_instance = Cohort.objects.create(
            study=study,
            name=name,
            study_length=study_length,
            export_data=export_data
            )