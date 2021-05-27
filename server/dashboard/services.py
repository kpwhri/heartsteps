import requests
# from push_messages.clients import OneSignalClient
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from participants.models import Study, Cohort, Participant
from push_messages.services import PushMessageService
from push_messages.models import Device
from hourly_tasks.models import HourlyTask

import random
import datetime

from nlm.models import StudyType, CohortAssignment, PreloadedLevelSequenceFile
import pprint
import uuid

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
            
    def send_notification(self, device_ids):
        for device_id in device_ids:
            device_id_single = [device_id]
            try:
                message_response_id = self.__send(device_id = device_id_single,
                        body = "test body",
                        title = "test title",
                        collapse_subject = "test collapse_subject",
                        data = {}
                    )
                return message_response_id
            except Exception as err:
                print("Exception thrown: {}".format(err))
                return None




    def set_device_token(self, username, player_id):
        user = User.objects.get(username=username)
        
        Device.objects.filter(user=user).delete()
        newDevice = Device.objects.create(user=user, active=True, token=player_id, type="onesignal")
        
        return newDevice




class DevService:
    class ArgumentError(RuntimeError):
        pass
    
    class NotificationSendError(RuntimeError):
        pass
    
    def __init__(self, user):
        self.user = user
        
    def __get_random_name(self, heading, digits, space=False):
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
                                    'devices': devices,
                                    'devices_text': ', '.join(d['token'] for d in devices)
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
    
    def get_participant_users_dict(self):
        participant_users_dict = []
        study_query = self.get_all_studies_query()
        if study_query:
            for study in study_query.all():
                cohort_query = self.get_all_cohorts_query(study)
                if cohort_query:
                    for cohort in cohort_query.all():
                        participant_query = self.get_all_participants_query(cohort)
                        if participant_query:
                            for participant in participant_query.all():
                                if participant and participant.user:
                                    participant_users_dict.append({
                                        'username': participant.user.username, 
                                        'study': {'id': study.id, 'name': study.name}, 
                                        'cohort': {'id': cohort.id, 'name': cohort.name}
                                    })
        
        return participant_users_dict
    
    
    
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
        study_instance.admins.add(self.user)
        study_instance.save()
        
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
                            enrollment_token = self.__get_random_name("t", 8, space=False)
                            study_start_date = "2021-04-01"
                            username = self.__get_random_name("user", 10, space=False)
                            new_user = User.objects.create(username=username)
                            heartsteps_id = username
                            token = self.__get_random_name("token", 10)
                            
                            participant = self.__create_participant(cohort, heartsteps_id, enrollment_token, study_start_date, new_user)
                            
                            new_device = Device.objects.create(user=new_user, token=token, active=True, type='onesignal')
                            
                            participants.append(participant)
                
        return "{} participants for all debug studies are created:{}".format(len(participants), participants) 

    def __create_participant(self, cohort, heartsteps_id, enrollment_token, study_start_date, user):
        participant_instance = Participant.objects.create(
                                cohort=cohort,
                                heartsteps_id=heartsteps_id,
                                enrollment_token = enrollment_token,
                                study_start_date = study_start_date,
                                user = user
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
    
    def get_user_by_username(self, username):
        try:
            user = User.objects.filter(username=username).first()
        
            return user
        except:
            return None
    
    def get_distinct_device_tokens_by_user(self, user):
        if user:
            try:
                devices = Device.objects.filter(user=user).all()
                tokens = [device.token for device in devices]
                tokens = list(set(tokens))
                return tokens
            except:
                raise DevService.ArgumentError()
        else:
            raise DevService.ArgumentError()
        
    def __generate_wordy_message(self, wordbase, number_of_words):
        wordlist = []
        
        for i in range(number_of_words):
            wordlist.append("{}{}".format(wordbase, i))
        
        return " ".join(wordlist)
        
    def send_notification_by_user(self, user):
        service = PushMessageService(user = user)
        message = service.send_notification(
            body = self.__generate_wordy_message("Body", 30),
            title = self.__generate_wordy_message("Title", 20),
            collapse_subject = 'Dev Test Collapse Subject',
            data = {}
        )
        return message

    def send_typed_notification_by_user(self, user, notification_type=None):
        if not notification_type:
            notification_type = "short_body_title"
        
        service = PushMessageService(user = user)
        
        if notification_type == "body_only":
            message = service.send_notification(
                "Hi, this is a test message.",
                data={}
            )
        elif notification_type == "short_body_title":
            message = service.send_notification(
                body = "test body",
                title = "test title"
            )
        elif notification_type == "long_body_title":
            message = service.send_notification(
                body = self.__generate_wordy_message("Body", 30),
                title = self.__generate_wordy_message("Title", 20)                
            )
        elif notification_type == "url1":
            message = service.send_notification(
                "https://www.google.com"
            )
        elif notification_type == "url2":
            message = service.send_notification(
                "https://www.heartsteps.net"
            )
        elif notification_type == "url3":
            message = service.send_notification(
                "https://www.heartsteps.net/settings"
            )
        
        # messages.add_message(request, messages.SUCCESS, 'Message sent')
        return message


    def get_cohort_dict(self):
        study_query = self.get_all_studies_query()
        cohorts = []
        if study_query:
            for study in study_query.all():
                cohort_query = self.get_all_cohorts_query(study)
                if cohort_query:
                    for cohort in cohort_query.all():
                        cohorts.append({
                            'id': cohort.id,
                            'study': {
                                'id': study.id,
                                'name': study.name
                            },
                            'name': cohort.name
                        })
        return cohorts
    
    def get_cohort_by_id(self, cohort_id):
        cohort = Cohort.objects.get(id=cohort_id)
        
        return cohort
    
    
    def get_all_crontabs(self):
        crontabs = CrontabSchedule.objects.all()
        
        return list(crontabs)
    
    def get_all_periodic_tasks(self):
        periodic_tasks = PeriodicTask.objects.all()
        
        return list(periodic_tasks)
    
    def get_all_hourly_tasks(self):
        hourly_tasks = HourlyTask.objects.all()
        
        return list(hourly_tasks)
    
    def create_task(self, name, task='nlm.tasks.nlm_base_hourly_task', minute=0, arguments={}):
        return HourlyTask.create_hourly_task(
            user = self.user,
            category = 'example',
            task = task,
            name = name,
            arguments = arguments,
            minute = minute
        )
        
    def create_sample_hourly_tasks(self):
        for minute in range(0, 60):
            self.create_task(name="Sample Hourly Task: minute={}".format(minute), minute=minute, arguments={'parameters': 
                    {
                        "minute": minute
                    }            
                })
    
    def delete_hourly_task_by_id(self, hourly_task_id):
        return HourlyTask.objects.get(id=hourly_task_id).delete()
    
    def get_all_hourly_tasks_query(self):
        return HourlyTask.objects.filter(user=self.user)
    
    def get_hourly_tasks_dict(self):
        query = self.get_all_hourly_tasks_query()
        
        hourly_tasks = []
        if query:
            for item in query.all():
                name = "(no name)"
                if item.task:
                    name = item.task.name
                    
                hourly_tasks.append({
                    "id": item.id,
                    "name": name,
                    "str": item.__str__
                })
        
        return hourly_tasks
    
    def delete_all_hourly_tasks(self):
        query = self.get_all_hourly_tasks_query()
        for hourly_task in query.all():
            hourly_task.task.delete()
            
    def design_test_study(self):
        objlist = []
            
        # Study Type
        test_study_type, _ = StudyType.objects.get_or_create(
            name="NLM",
            frequency=StudyType.HOURLY
        )
        test_study_type.admin = [self.user]
        objlist.append(test_study_type)
        
        # Study
        test_study = Study.objects.create(
            name = self.__get_random_name("nlm_test_", 8)
        )
        test_study.admin = [self.user]
        objlist.append(test_study)
        
        # Cohort
        test_cohort = Cohort.objects.create(
            name = self.__get_random_name("nlm_test_cohort_", 8),
            study = test_study
        )
        objlist.append(test_cohort)
        
        # Cohort Assignment
        test_cohort_assignment = CohortAssignment.objects.create(
            cohort = test_cohort,
            studytype = test_study_type
        )
        objlist.append(test_cohort_assignment)
        
        # User
        test_user = User.objects.create(
            username = self.__get_random_name("nlm_test_user_", 8)
        )
        objlist.append(test_user)
        
        # Participant
        test_participant = Participant.objects.create(
            heartsteps_id = self.__get_random_name("nlm_test_pcp_", 4),
            enrollment_token = self.__get_random_name("test_", 2),
            birth_year = "2021",
            cohort = test_cohort,
            user=test_user
        )
        objlist.append(test_participant)
        
        # Device
        Device.objects.filter(user=test_user).delete()
        test_device = Device.objects.create(
            user=test_user,
            active=True, 
            token="5d851ed2-77f3-4205-b377-12557f7a2918", 
            type="onesignal"
        )
        objlist.append(test_device)
        
        return objlist
    
    def view_test_study(self):
        lines = []
        
        # StudyType
        study_type_list, success = self.view_modelclass(lines, 
                                       StudyType, {
            'name': 'NLM'
        })
        if not success:
            return lines
        test_study_type = study_type_list[0]
        
        # Study
        _, success = self.view_modelclass(lines, 
                                       Study, {
            'name__startswith': 'nlm_test_'
        })
        if not success:
            return lines
        
        # Cohort
        _, success = self.view_modelclass(lines, 
                                       Cohort, {
            'name__startswith': 'nlm_test_cohort_'
        })
        if not success:
            return lines
        
        
        # CohortAssignment
        test_cohort_assignment_list, success = self.view_modelclass(lines, 
                                       CohortAssignment, {
            'studytype': test_study_type
        })
        if not success:
            return lines
        test_cohort_assignment = test_cohort_assignment_list[0]
        
        # User
        test_users, success = self.view_modelclass(lines, 
                                       User, {
            'username__startswith': "nlm_test_user_"
        })
        if not success:
            return lines
        
        # Participant
        test_participants, success = self.view_modelclass(lines, 
                                       Participant, {
            'user__username__startswith': "nlm_test_user_"
        })
        if not success:
            return lines
        
        # Device
        test_devices, success = self.view_modelclass(lines, 
                                       Device, {
            'user__username__startswith': "nlm_test_user_"
        })
        if not success:
            return lines
        
        
        return lines

    def view_modelclass(self, lines, modelclass, filter_dict):
        modelname = modelclass.__name__
        success = True
        try:
            itemlist = modelclass.objects.filter(**filter_dict).all()
            if itemlist:    
                for an_item in itemlist:
                    lines.append("{} found: {}".format(modelname, an_item))
            else:
                raise models.Model.DoesNotExist
        except:
            lines.append("no {} found".format(modelname))
            success = False
        return itemlist, success
        
        
    def delete_test_study(self):
        StudyType.objects.get(name="NLM").delete()
        
        Study.objects.filter(name__startswith='nlm_test_').delete()
        # Cohort, CohortAssignment will be deleted by cascading
        
        User.objects.filter(username__startswith='nlm_test_user_').delete()
        # Participant will be deleted by cascading
    
    def upload_level_csv(self, filename, nickname, lines):
        return PreloadedLevelSequenceFile.insert(self.user, filename, nickname, lines)