import requests
# from push_messages.clients import OneSignalClient
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

from participants.models import Study, Cohort, Participant
from push_messages.models import Device

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
    
    def set_device_token(self, username, player_id):
        user = User.objects.get(username=username)
        
        device = Device.objects.create(
            type="OneSignal",
            token=player_id,
            user=user
        )
        
        return device




class DevService:
    def __init__(self, user):
        self.user = user
        
    def __get_random_name(self, heading, digits, space=True):
        formatstr = '%0{}X'.format(digits)
        randhex = formatstr % random.randrange(16**digits)
        if space:
            return "{} {}".format(heading, randhex)
        else:
            return "{}{}".format(heading, randhex)
    
    def get_all_studies_query(self, debug=False):
        if self.user.is_superuser:
            study_query = Study.objects
        else:
            study_query = Study.objects.filter(admins=self.user)
        
        if debug:
            study_query = study_query.filter(contact_name__startswith="Debugger", admins=self.user)
            
        return study_query
    
    def get_all_cohorts_query(self, study, debug=False):
        cohort_query = study.cohort_set
        if debug:
            cohort_query = cohort_query.filter(name__startswith="Debug Cohort")

        return cohort_query
    
    def get_all_participants_query(self, cohort, debug=False):
        participant_query = cohort.participant_set
        if debug:
            participant_query = participant_query.filter(heartsteps_id__startswith="id")
        
        return participant_query
        
    def get_all_devices_query_by_participant(self, participant):
        if participant:        
            puser = participant.user
            if puser:
                return puser.device_set
            else:
                return None
        else:
            raise DevService.ArgumentError()
    
    def get_all_admin_colleagues(self):
        study_query = self.get_all_studies_query()
        if study_query:
            studies = study_query.all()
            colleagues = []
            
            for study in studies:
                for colleague in study.admins.all():
                    colleagues.append(colleague)
            
            colleagues = list(set(colleagues))
            
            return colleagues
        else:
            return []
    
    def get_study_cohort_participant_device_dict(self, study_query):
        studies = []
        if study_query:
            for study in study_query.all():
                cohorts = self.get_cohort_participant_device_dict(study)
                studies.append({
                    'id': study.id,
                    'name': study.name,
                    'cohorts': cohorts
                })
        return studies

    def get_cohort_participant_device_dict(self, study):
        cohorts = []
        cohort_query = self.get_all_cohorts_query(study)
        if cohort_query:
            for cohort in cohort_query.all():
                participants = self.get_participant_device_dict(cohort)
                cohorts.append({
                            'id': cohort.id,
                            'name': cohort.name,
                            'participants': participants
                        })
        return cohorts

    def get_participant_device_dict(self, cohort):
        participants = []
        participant_query = self.get_all_participants_query(cohort)
        if participant_query:
            for participant in participant_query.all():
                devices = self.get_device_by_participant_dict(participant)
                participants.append({
                                    'heartsteps_id': participant.heartsteps_id,
                                    'enrollment_token': participant.enrollment_token,
                                    'devices': devices
                                })
        return participants

    def get_device_by_participant_dict(self, participant):
        devices = []
        device_query = self.get_all_devices_query_by_participant(participant)
        if device_query:
            for device in device_query.all():
                devices.append({
                                    'id': device.id,
                                    'user': device.user,
                                    'token': device.token,
                                    'active': device.active,
                                    'type': device.type
                                })
        return devices
    
    def get_colleague_dict(self):
        colleagues = []
        _colleagues = self.get_all_admin_colleagues()
        for user in _colleagues:
            colleagues.append({
                "username": user.username,
            })
        return colleagues
    
    def create_debug_study(self, number_of_studies):
        studies = []
        for i in range(number_of_studies):
            study_name = self.__get_random_name("Debug Study", 10)
            contact_name = "Debugger"
            contact_number = "8581234567"
            baseline_period = 7

            study = self.__create_study(study_name, contact_name, contact_number, baseline_period)
            studies.append(study)

        return "{} studies are created: {}".format(len(studies), str(studies))

    def __create_study(self, study_name, contact_name, contact_number, baseline_period):
        study_instance = Study.objects.create(name=study_name, 
                                            contact_name=contact_name,
                                            contact_number=contact_number,
                                            baseline_period=baseline_period  
                                            )
        study_instance.admins.set([self.user])
        
        return study_instance
    
    def create_debug_cohort(self, number_of_cohorts):
        study_query = self.get_all_studies_query(debug=True)
        cohorts = []
        if study_query:
            for study in study_query.all():
                for i in range(number_of_cohorts):
                    cohort_name = self.__get_random_name("Debug Cohort", 10)
                    study_length = 365
                    export_data = False                    

                    cohort = self.__create_cohort(study, cohort_name, study_length, export_data)
                    cohorts.append(cohort)
                
        return "{} cohorts for all debug studies are created: {}".format(len(cohorts), cohorts)  
    
    def __create_cohort(self, study, cohort_name, study_length, export_data):
        cohort_instance = Cohort.objects.create(
            study=study,
            name=cohort_name,
            study_length=study_length,
            export_data=export_data
            )
    
    def create_debug_participant(self, number_of_participants):
        participants = []
        study_query = self.get_all_studies_query(debug=True)
        if study_query:
            for study in study_query.all():
                cohorts_query = self.get_all_cohorts_query(study, debug=True)
                if cohorts_query:
                    for cohort in cohorts_query.all():    
                        for i in range(number_of_participants):
                            heartsteps_id = self.__get_random_name("id", 10, space=False)
                            enrollment_token = self.__get_random_name("t", 8, space=False)
                            study_start_date = "2021-04-01"
                            
                            participant = self.__create_participant(cohort, heartsteps_id, enrollment_token, study_start_date)
                            participants.append(participant)
                
        return "{} participants for all debug studies are created:{}".format(len(participants), participants) 

    def __create_participant(self, cohort, heartsteps_id, enrollment_token, study_start_date):
        participant_instance = Participant.objects.create(
                                cohort=cohort,
                                heartsteps_id=heartsteps_id,
                                enrollment_token = enrollment_token,
                                study_start_date = study_start_date
                            ) 
        return participant_instance
    
    def clear_debug_study(self):
        results = self.get_all_studies_query(debug=True).delete()
    
        return "All debug Studies are deleted: {}".format(results)
    
    def clear_debug_participant(self):
        delete_results = []
        study_query = self.get_all_studies_query(debug=True)
        if study_query:
            for study in study_query.all():
                cohorts_query = self.get_all_cohorts_query(study, debug=True)
                if cohorts_query:
                    for cohort in cohorts_query.all():    
                        participant_query = self.get_all_participants_query(cohort, debug=True)
                        delete_results.append(participant_query.delete())
                        
        return "All debug Participants are deleted:{}".format(delete_results)
    
    def clear_orphan_debug_participant(self):
        orphan_participant_query = Participant.objects.filter(heartsteps_id__startswith="id")
        
        result = orphan_participant_query.delete()
        
        return "Orphan Participants are deleted: {}".format(result)
    
    
    
