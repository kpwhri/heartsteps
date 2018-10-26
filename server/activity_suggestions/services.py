import requests
from datetime import timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from randomization.services import DecisionService, DecisionContextService, DecisionMessageService

from activity_suggestions.models import ActivityServiceRequest

class ActivitySuggestionService():
    """
    Handles state and requests between activity-suggestion-service and
    heartsteps-server for a specific participant.
    """

    def __init__(self, user):
        self.__user = user

        if not hasattr(settings,'ACTIVITY_SUGGESTION_SERVICE_URL'):
            raise ImproperlyConfigured('No activity suggestion service url')
        else:
            self.__base_url = settings.ACTIVITY_SUGGESTION_SERVICE_URL

    def make_request(self, uri, data):
        url = urljoin(self.__base_url, uri)
        request_record = ActivityServiceRequest(
            user = self.__user,
            url = url,
            request_data = data,
            request_time = timezone.now()
        )
        
        response = requests.post(url, data=data)
        response_data = response.json()

        request_record.response_code = response.status_code
        request_record.response_data = response_data
        request_record.response_time = timezone.now()
        request_record.save()

        return response_data

    def initialize(self, date):
        dates = [date - timedelta(days=offset) for offset in range(7)]
        self.make_request('initialize', {
            'userId': self.__user.id,
            'appClicksArray': [self.get_clicks(date) for date in dates],
            'totalStepsArray': [self.get_steps(date) for date in dates],
            'availMatrix': [self.get_availabilities(date) for date in dates],
            'tempratureMatrix': [self.get_temperatures(date) for date in dates],
            'preStepsMatrix': [self.get_pre_steps(date) for date in dates],
            'postStepsMatrix': [self.get_post_steps(date) for date in dates]
        })

    def update(self, date):
        response = self.make_request('nightly', {
            'userId': [self.__user.id],
            'studyDay': [self.get_study_day_number()],
            'appClick': [self.get_clicks(date)],
            'totalSteps': [self.get_steps(date)],
            'priorAnti': [False],
            'lastActivity': [False],
            'temperatureArray': self.get_temperatures(date),
            'preStepArray': self.get_pre_steps(date),
            'postStepsArray': self.get_post_steps(date)
        })
    
    def decide(self, decision):
        response = self.make_request('decision', {
            'userId': self.__user.id,
            'studyDay': self.get_study_day_number(),
            'decisionTime': self.categorize_activity_suggestion_time(decision),
            'availability': False,
            'priorAnti': False,
            'lastActivity': False,
            'location': self.categorize_location(decision)
        })

        if response.status_code is not 200:
            return False
        response_data = response.json()
        decision.a_it = response_data['send']
        decision.pi_id = response_data['probability']
        decision.save()
            

    def get_clicks(self, date):
        return None

    def get_steps(self, date):
        return None

    def get_availabilities(self, date):
        return [False for offset in range(5)]

    def get_temperatures(self, date):
        return [0 for offset in range(5)]

    def get_pre_steps(self, date):
        return [0 for offset in range(5)]

    def get_post_steps(self, date):
        return [0 for offset in range(5)]

    def get_study_day_number(self):
        return 2
    
    def categorize_activity_suggestion_time(self, decsision):
        return 1

    def categorize_location(self, decision):
        return 0

class ActivitySuggestionDecisionService(DecisionContextService, DecisionMessageService):
    
    def decide(self):

        try:
            service = ActivitySuggestionService(self.user)
            service.decide(decision)
        except ImproperlyConfigured:
            self.decision.a_it = True
            self.decision.pi_it = 1
            self.decision.save()

        return self.decision.a_it
