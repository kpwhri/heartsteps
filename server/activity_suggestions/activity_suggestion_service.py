import requests
import json
import pytz
from datetime import timedelta, datetime
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType

from fitbit_api.models import FitbitDay, FitbitMinuteStepCount
from randomization.models import Decision, DecisionContext
from weather.models import WeatherForecast

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
        temperatures = []
        forecast_content_type = ContentType.objects.get_for_model(WeatherForecast)
        decisions = self.get_decisions_for(date)
        for time_category in SuggestionTime.TIMES:
            if time_category in decisions:
                forecasts = DecisionContext.objects.filter(
                    decision = decisions[time_category],
                    content_type = forecast_content_type
                ).all()
                if not len(forecasts):
                    raise ValueError("No Weather Forecast")
                if len(forecasts) == 1:
                    temperatures.append(forecasts[0].content_object.temperature_celcius)
                else:
                    forecast_temperatures = [forecast.content_object.temperature_celcius for forecast in forecasts]
                    average_temperature = sum(forecast_temperatures)/len(forecast_temperatures)
                    temperatures.append(average_temperature)
            else:
                temperatures.append(None)
        return temperatures

    def get_pre_steps(self, date):
        decisions = self.get_decisions_for(date)
        steps = []
        for time_category in SuggestionTime.TIMES:
            if time_category in decisions:
                decision = decisions[time_category]
                step_count = self.get_steps_before(decision.time)
                steps.append(step_count)
            else:
                steps.append(None)
        return steps

    def get_post_steps(self, date):
        decisions = self.get_decisions_for(date)
        steps = []
        for time_category in SuggestionTime.TIMES:
            if time_category in decisions:
                decision = decisions[time_category]
                step_count = self.get_steps_after(decision.time)
                steps.append(step_count)
            else:
                steps.append(None)
        return steps

    def get_decisions_for(self, date):
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
                decision_times[time_category] = decision
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
