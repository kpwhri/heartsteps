import requests
import json
import pytz
from datetime import timedelta, datetime
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from fitbit_api.models import FitbitDay, FitbitMinuteStepCount
from randomization.models import Decision

from activity_suggestions.models import Configuration, ServiceRequest, SuggestionTime

class ActivitySuggestionService():
    """
    Handles state and requests between activity-suggestion-service and
    heartsteps-server for a specific participant.
    """

    class NotInitialized(Exception):
        pass

    def __init__(self, configuration):
        self.__configuration = configuration
        self.__user = configuration.user
        if not hasattr(settings,'ACTIVITY_SUGGESTION_SERVICE_URL'):
            raise ImproperlyConfigured('No activity suggestion service url')
        else:
            self.__base_url = settings.ACTIVITY_SUGGESTION_SERVICE_URL

    def make_request(self, uri, data):
        url = urljoin(self.__base_url, uri)
        data['userId'] = self.__user.username
        request_record = ServiceRequest(
            user = self.__user,
            url = url,
            request_data = json.dumps(data),
            request_time = timezone.now()
        )

        response = requests.post(url, data=data)

        request_record.response_code = response.status_code
        request_record.response_data = response.text
        request_record.response_time = timezone.now()
        request_record.save()

        return response.text

    def initialize(self):
        date = timezone.now()
        dates = [date - timedelta(days=offset) for offset in range(7)]
        data = {
            'appClicksArray': [self.get_clicks(date) for date in dates],
            'totalStepsArray': [self.get_steps(date) for date in dates],
            'availMatrix': [{'avail': self.get_availabilities(date)} for date in dates],
            'temperatureMatrix': [{'temp': self.get_temperatures(date)} for date in dates],
            'preStepsMatrix': [{'steps': self.get_pre_steps(date)} for date in dates],
            'postStepsMatrix': [{'steps': self.get_post_steps(date)} for date in dates]
        }
        self.make_request('initialize',
            data = data
        )
        self.__configuration.enabled = True
        self.__configuration.save()

    def update(self, date):
        if not self.__configuration.enabled:
            raise self.NotInitialized()
        data = {
            'studyDay': self.get_study_day_number(),
            'appClick': self.get_clicks(date),
            'totalSteps': self.get_steps(date),
            'priorAnti': False,
            'lastActivity': False,
            'temperatureArray': self.get_temperatures(date),
            'preStepArray': self.get_pre_steps(date),
            'postStepsArray': self.get_post_steps(date)
        }
        response = self.make_request('nightly',
            data = data
        )
    
    def decide(self, decision):
        if not self.__configuration.enabled:
            raise self.NotInitialized()
        response = self.make_request('decision',
            data = {
                'studyDay': self.get_study_day_number(),
                'decisionTime': self.categorize_activity_suggestion_time(decision),
                'availability': False,
                'priorAnti': False,
                'lastActivity': False,
                'location': self.categorize_location(decision)
            }
        )

        if response.status_code is not 200:
            return False
        response_data = response.json()
        decision.a_it = response_data['send']
        decision.pi_id = response_data['probability']
        decision.save()
            

    def get_clicks(self, date):
        return 0

    def get_steps(self, date):
        try:
            day = FitbitDay.objects.get(
                account__user = self.__user,
                date__year = date.year,
                date__month = date.month,
                date__day = date.day
            )
        except FitbitDay.DoesNotExist:
            return None
        return day.total_steps        

    def get_availabilities(self, date):
        return [False for offset in range(5)]

    def get_temperatures(self, date):
        return [0 for offset in range(5)]

    def get_pre_steps(self, date):
        decision_times = self.get_activity_suggestion_times_for(date)
        steps = []
        for time_category in SuggestionTime.TIMES:
            if time_category in decision_times:
                step_count = self.get_steps_before(decision_times[time_category])
                steps.append(step_count)
            else:
                steps.append(None)
        return steps

    def get_post_steps(self, date):
        decision_times = self.get_activity_suggestion_times_for(date)
        steps = []
        for time_category in SuggestionTime.TIMES:
            if time_category in decision_times:
                step_count = self.get_steps_after(decision_times[time_category])
                steps.append(step_count)
            else:
                steps.append(None)
        return steps

    def get_activity_suggestion_times_for(self, date):
        decision_times = {}

        start_time = datetime(date.year, date.month, date.day, 0, 0, tzinfo=self.__configuration.timezone)
        end_time = start_time + timedelta(days=1)
        decision_query = Decision.objects.filter(
            user=self.__user,
            tags__tag='activity suggestion',
            time__range = [start_time, end_time]
        )
        for time_category in SuggestionTime.TIMES:
            try:
                decision = decision_query.filter(tags__tag=time_category).get()
                decision_times[time_category] = decision.time
            except Decision.DoesNotExist:
                continue
        return decision_times

    def get_steps_before(self, time):
        return self.get_steps_between(time - timedelta(minutes=30), time)

    def get_steps_after(self, time):
        return self.get_steps_between(time, time + timedelta(minutes=30))

    def get_steps_between(self, start_time, end_time):
        step_counts = FitbitMinuteStepCount.objects.filter(
            account__user = self.__user,
            time__range = (start_time, end_time)
        ).all()
        total_steps = 0
        for step_count in step_counts:
            total_steps += step_count.steps
        return total_steps

    def get_study_day_number(self):
        difference = timezone.now() - self.__user.date_joined
        return difference.days + 1
    
    def categorize_activity_suggestion_time(self, decsision):
        return 1

    def categorize_location(self, decision):
        return 0
