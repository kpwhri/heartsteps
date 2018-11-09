import requests, json, pytz
from datetime import datetime, timedelta
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType

from fitbit_api.models import FitbitDay, FitbitMinuteStepCount
from push_messages.models import MessageReceipt, Message
from randomization.models import Decision, DecisionContext
from randomization.services import DecisionService, DecisionContextService, DecisionMessageService
from weather.models import WeatherForecast

from activity_suggestions.models import Configuration, ServiceRequest, SuggestionTime

class ActivitySuggestionDecisionService(DecisionContextService, DecisionMessageService):

    def determine_availability(self):
        if self.get_fitbit_step_count() > 250:
            return False
        return True
    
    def get_fitbit_step_count(self):
        start_time = self.decision.time - timedelta(minutes=20)
        step_counts = FitbitMinuteStepCount.objects.filter(
            account__user = self.decision.user,
            time__range = [start_time, self.decision.time]
        ).all()
        total_steps = 0
        for step_count in step_counts:
            total_steps += step_count.steps
        return total_steps

    def decide(self):
        try:
            service = ActivitySuggestionService(self.user)
            service.decide(self.decision)
        except ImproperlyConfigured:
            self.decision.decide()
        return self.decision.a_it

class ActivitySuggestionService():
    """
    Handles state and requests between activity-suggestion-service and
    heartsteps-server for a specific participant.
    """

    class Unavailable(ImproperlyConfigured):
        pass

    class NotInitialized(ImproperlyConfigured):
        pass

    def __init__(self, configuration):
        self.__configuration = configuration
        self.__user = configuration.user
        if not hasattr(settings,'ACTIVITY_SUGGESTION_SERVICE_URL'):
            raise self.Unavailable("No ACTIVITY_SUGGESTION_SERVICE_URL")
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

        return json.loads(response.text)

    def initialize(self, date):
        if not hasattr(settings, 'ACTIVITY_SUGGESTION_INITIALIZATION_DAYS'):
            raise ImproperlyConfigured('No initialization days specified')
        else:
            initialization_days = settings.ACTIVITY_SUGGESTION_INITIALIZATION_DAYS
        dates = [date - timedelta(days=offset) for offset in range(initialization_days)]
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
        self.__configuration.service_initialized = True
        self.__configuration.save()

    def update(self, date):
        if not self.__configuration.service_initialized:
            raise self.NotInitialized()

        postdinner_decision = Decision.objects.filter(
            user = self.__user,
            time__range = [
                self.__configuration.get_start_of_day(date),
                self.__configuration.get_end_of_day(date)
            ],
            tags__tag = 'activity suggestion',
        ).filter(
            tags__tag = SuggestionTime.POSTDINNER
        ).first()
        if postdinner_decision:
            last_activity = self.decision_was_received(postdinner_decision)
            prior_anti = self.was_notified_between(
                postdinner_decision.time + timedelta(minutes=1),
                self.__configuration.get_end_of_day(date)
            )
        else:
            prior_anti = False 
            last_activity = False

        data = {
            'studyDay': self.get_study_day(date),
            'appClick': self.get_clicks(date),
            'totalSteps': self.get_steps(date),
            'priorAnti': prior_anti,
            'lastActivity': last_activity,
            'temperatureArray': self.get_temperatures(date),
            'preStepsArray': self.get_pre_steps(date),
            'postStepsArray': self.get_post_steps(date)
        }
        response = self.make_request('nightly',
            data = data
        )
    
    def decide(self, decision):
        if not self.__configuration.service_initialized:
            raise self.NotInitialized()
        decision_service = ActivitySuggestionDecisionService(decision)
        response = self.make_request('decision',
            data = {
                'studyDay': self.get_study_day(decision.time),
                'decisionTime': self.categorize_activity_suggestion_time(decision),
                'availability': decision_service.determine_availability(),
                'priorAnti': self.notified_since_previous_decision(decision),
                'lastActivity': self.previous_decision_was_received(decision),
                'location': decision_service.get_location_context()
            }
        )
        decision.a_it = response['send']
        decision.pi_id = response['probability']
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
        for decision in self.get_decisions_for(date):
            decision_service = ActivitySuggestionDecisionService(decision)
            yield decision_service.determine_availability()

    def get_temperatures(self, date):
        temperatures = []
        forecast_content_type = ContentType.objects.get_for_model(WeatherForecast)
        decisions = self.get_decisions_for(date)
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            service = ActivitySuggestionDecisionService(decision)
            forecasts = service.get_forecasts()

            forecast_temperatures = [forecast.temperature for forecast in forecasts]
            average_temperature = sum(forecast_temperatures)/len(forecast_temperatures)
            temperature_celcius = (average_temperature - 32)/1.8
            temperatures.append(temperature_celcius)
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

    def get_time_range(self, date):
        start_time = datetime(date.year, date.month, date.day, 0, 0, tzinfo=self.__configuration.timezone)
        end_time = start_time + timedelta(days=1)
        return [start_time, end_time]

    def get_decisions_for(self, date):
        decision_times = {}

        decision_query = Decision.objects.filter(
            user=self.__user,
            tags__tag='activity suggestion',
            time__range = self.get_time_range(date)
        )
        for time_category in SuggestionTime.TIMES:
            try:
                decision = decision_query.filter(tags__tag=time_category).get()
            except Decision.DoesNotExist:
                decision = self.create_decision_for(date, time_category)
            decision_times[time_category] = decision
        return decision_times

    def create_decision_for(self, date, time_category):
        try:
            suggestion_time = SuggestionTime.objects.get(
                user = self.__user,
                category = time_category
            )
        except SuggestionTime.DoesNotExist:
            raise ImproperlyConfigured("%s doesn't have suggestion time for %s" % (self.__user, time_category))
        time = datetime(
            year = date.year,
            month = date.month,
            day = date.day,
            hour = suggestion_time.hour,
            minute = suggestion_time.minute,
            tzinfo=self.__configuration.timezone
        )
        decision = Decision.objects.create(
            user = self.__user,
            time = time,
            a_it = False,
            pi_it = 0
        )
        decision.add_context('activity_suggestion')
        decision.add_context('imputed')
        decision.add_context(time_category)
        return decision


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

    def get_study_day(self, date):
        difference = date - self.__user.date_joined
        return difference.days + 1
    
    def categorize_activity_suggestion_time(self, decision):
        for tag in decision.get_context():
            if tag in SuggestionTime.TIMES:
                return SuggestionTime.TIMES.index(tag) + 1
        raise ValueError('Decision does not have suggestion time')

    def previous_decision_was_received(self, decision):
        previous_decision = self.get_previous_decision(decision)
        return self.decision_was_received(previous_decision)

    def decision_was_received(self, decision):
        if not decision:
            return False
        if not hasattr(decision, 'message'):
            return False
        try:
            message_receipt = MessageReceipt.objects.get(
                message = decision.message.sent_message,
                type = MessageReceipt.RECEIVED
            )
            return True
        except MessageReceipt.DoesNotExist:
            return False

    def get_previous_decision(self, decision):
        return Decision.objects.filter(
            user = decision.user,
            tags__tag = "activity suggestion",
            time__range = [
                self.__configuration.get_start_of_day(decision.time),
                decision.time - timedelta(minutes=1)
            ]
        ).first()

    def notified_since_previous_decision(self, decision):
        previous_decision = self.get_previous_decision(decision)
        if previous_decision:
            return self.was_notified_between(
                previous_decision.time + timedelta(minutes=1),
                decision.time - timedelta(minutes=1)
            )
        else:
            return self.was_notified_between(
                self.__configuration.get_start_of_day(decision.time),
                decision.time - timedelta(minutes=1)
            )

    def was_notified_between(self, start, end):
        messages_sent = MessageReceipt.objects.filter(
            type = MessageReceipt.SENT,
            message__message_type = Message.NOTIFICATION,
            time__range = [start, end]
        ).count()
        if messages_sent > 0:
            return True
        else:
            return False
