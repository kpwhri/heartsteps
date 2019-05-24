import requests, json, pytz
from datetime import datetime, timedelta, date as datetime_date
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType

from anti_sedentary.models import AntiSedentaryDecision
from fitbit_api.models import FitbitAccountUser
from fitbit_activities.models import FitbitDay, FitbitMinuteStepCount
from locations.models import Place
from locations.services import LocationService
from push_messages.models import MessageReceipt, Message
from randomization.models import DecisionContext
from randomization.services import DecisionService, DecisionContextService, DecisionMessageService
from weather.models import WeatherForecast
from watch_app.models import StepCount as WatchStepCount

from .models import Configuration
from .models import SuggestionTime
from .models import WalkingSuggestionDecision
from .models import WalkingSuggestionMessageTemplate
from .models import WalkingSuggestionServiceRequest as ServiceRequest

class WalkingSuggestionTimeService:

    class Unavailable(ImproperlyConfigured):
        pass

    def __init__(self, configuration=None, user=None, username=None):
        try:
            if username:
                configuration = Configuration.objects.get(user__username=username)
            if user:
                configuration = Configuration.objects.get(user=user)
        except Configuration.DoesNotExist:
            raise WalkingSuggestionTimeService.Unavailable('Configuration not found')
        if not configuration:
            raise WalkingSuggestionTimeService.Unavailable('Not configured')
        if not configuration.enabled:
            raise WalkingSuggestionTimeService.Unavailable('Configuration disabled')
        self.__configuration = configuration
        self.__user = configuration.user

    def suggestion_time_category_available_at(self, time):
        category = self.suggestion_time_category_at(time)

        query = WalkingSuggestionDecision.objects.filter(
            user = self.__user,
            test = False,
            time__range = [
                self.__configuration.get_start_of_day(time),
                self.__configuration.get_end_of_day(time)
            ]
        )
        tags = [decision.category for decision in query.all()] 
        
        if category in tags:
            raise self.Unavailable('Time already taken')
        else:
            return category

    def suggestion_time_category_at(self, time):
        if not hasattr(settings,'WALKING_SUGGESTION_DECISION_WINDOW_MINUTES'):
            raise ImproperlyConfigured("Walking suggestion decision window minutes Unset")
        decision_window_minutes = int(settings.WALKING_SUGGESTION_DECISION_WINDOW_MINUTES)
        
        for suggestion_time in self.__configuration.suggestion_times:
            suggestion_time_today = suggestion_time.get_datetime_on(time)
            if time < suggestion_time_today:
                continue
            difference = time - suggestion_time_today
            if difference.seconds >= 0 and difference.seconds < decision_window_minutes*60:
                return suggestion_time.category
        return False

    def create_decision(self, category, time=None):
        if not time:
            time = timezone.now()
        if category not in SuggestionTime.TIMES:
            raise RuntimeError('Category is not suggestion time')

        decision = WalkingSuggestionDecision.objects.create(
            user = self.__user,
            time = timezone.now()
        )
        decision.add_context(category)
        return decision


class WalkingSuggestionDecisionService(DecisionContextService, DecisionMessageService):

    class DecisionDoesNotExist(ImproperlyConfigured):
        pass

    MESSAGE_TEMPLATE_MODEL = WalkingSuggestionMessageTemplate

    def __init__(self, decision):
        self.decision = decision
        self.user = decision.user
        try:
            self.__configuration = Configuration.objects.get(user=self.user)
            self.enabled = self.__configuration.enabled
        except Configuration.DoesNotExist:
            self.__configuration = None
            self.enabled = False

    def create_decision(user, category, time=None, test=False):
        if not time:
            time = timezone.now()
        decision = WalkingSuggestionDecision.objects.create(
            user = user,
            time = time,
            test = test
        )
        decision.add_context(category)
        return WalkingSuggestionDecisionService(decision)
    
    def get_decision(decision_id):
        try:
            decision = WalkingSuggestionDecision.objects.get(id=decision_id)
            return WalkingSuggestionDecisionService(decision)
        except WalkingSuggestionDecision.DoesNotExist:
            raise WalkingSuggestionDecisionService.DecisionDoesNotExist('Decision not found')

    def update_availability(self):
        if not self.enabled:
            self.decision.available = False
            self.decision.unavailable_reason = 'Walking suggestion configuration disabled'
            self.decision.save()
            return False

        if self.has_recent_walking_suggestion_treatment():
            self.decision.available = False
            self.decision.unavailable_reason = 'Recently treated walking suggestion decision'
            self.decision.save()
            return False

        if self.has_recent_anti_sedentary_treatment():
            self.decision.available = False
            self.decision.unavailable_reason = 'Recently treated anti sedentary decision'
            self.decision.save()
            return False

        step_counts = self.get_step_counts()
        if not step_counts:
            self.decision.available = False
            self.decision.unavailable_reason = 'No step counts recorded'
            self.decision.save()
            return False
        steps = 0
        for step_count in step_counts:
            steps += step_count.steps        
        if not hasattr(settings,'WALKING_SUGGESTION_DECISION_UNAVAILABLE_STEP_COUNT'):
            raise ImproperlyConfigured("Walking suggestion decision unavailable step count not set")
        max_step_count = int(settings.WALKING_SUGGESTION_DECISION_UNAVAILABLE_STEP_COUNT)
        if steps > max_step_count:
            self.decision.available = False
            self.decision.unavailable_reason = 'Recent step count above %d' % (max_step_count)
            self.decision.save()
            return False
        return True

    def has_recent_walking_suggestion_treatment(self):
        recent_treatments = WalkingSuggestionDecision.objects.filter(
            user = self.decision.user,
            treated = True,
            time__range = [
                self.decision.time - timedelta(minutes=60),
                self.decision.time
            ]
        ).count()
        if recent_treatments > 0:
            return True
        else:
            return False

    def has_recent_anti_sedentary_treatment(self):
        recent_treatments = AntiSedentaryDecision.objects.filter(
            user = self.decision.user,
            treated = True,
            time__range = [
                self.decision.time - timedelta(minutes=60),
                self.decision.time
            ]
        ).count()
        if recent_treatments > 0:
            return True
        else:
            return False

    def get_step_counts(self):
        if not hasattr(settings,'WALKING_SUGGESTION_DECISION_WINDOW_MINUTES'):
            raise ImproperlyConfigured("Walking suggestion decision window minutes not set")
        step_counts = WatchStepCount.objects.filter(
            user = self.user,
            start__gte = self.decision.time - timedelta(minutes=settings.WALKING_SUGGESTION_DECISION_WINDOW_MINUTES),
            end__lte = self.decision.time
        ).all()
        return list(step_counts)

    def get_message_template_query(self):
        return WalkingSuggestionMessageTemplate.objects

    def decide(self):
        if self.decision.test:
            self.decision.treated = True
            self.decision.treatment_probability = 1
            self.decision.save()
            return self.decision.treated
        if not self.enabled:
            self.decision.treated = False
            self.decision.treatment_probability = 0
            self.unavailable_reason = "Walking suggestion configuration disabled"
            self.decision.save()
            return False
        try:
            service = WalkingSuggestionService(self.__configuration)
            service.decide(self.decision)
        except ImproperlyConfigured:
            self.decision.decide()
        except WalkingSuggestionService.RequestError:
            self.decision.treated = False
            self.decision.treatment_probability = 0
            self.decision.available = False
            self.decision.unavailable_reason = "Walking suggestion service error"
            self.decision.save()
        return self.decision.a_it

class WalkingSuggestionService():
    """
    Handles state and requests between walking-suggestion-service and
    heartsteps-server for a specific participant.
    """

    class Unavailable(ImproperlyConfigured):
        pass

    class NotInitialized(ImproperlyConfigured):
        pass

    class RequestError(RuntimeError):
        pass

    def __init__(self, configuration=None, user=None, username=None):
        try:
            if username:
                configuration = Configuration.objects.get(user__username=username)
            if user:
                configuration = Configuration.objects.get(user=user)
        except Configuration.DoesNotExist:
            raise self.Unavailable('No configuration')

        self.__configuration = configuration
        self.__user = configuration.user

        if not hasattr(settings,'WALKING_SUGGESTION_SERVICE_URL'):
            raise self.Unavailable("No WALKING_SUGGESTION_SERVICE_URL")
        else:
            self.__base_url = settings.WALKING_SUGGESTION_SERVICE_URL
        if not self.__configuration.enabled:
            raise self.Unavailable('Walking suggestion configuration disabled')

    def make_request(self, uri, data):
        url = urljoin(self.__base_url, uri)
        data['userID'] = self.__user.username
        request_record = ServiceRequest(
            user = self.__user,
            url = url,
            name = 'WalkingSuggestionService: %s' % (uri),
            request_data = json.dumps(data),
            request_time = timezone.now()
        )

        response = requests.post(url, json=data)

        request_record.response_code = response.status_code
        request_record.response_data = response.text
        request_record.response_time = timezone.now()
        request_record.save()

        if response.status_code >= 400:
            raise self.RequestError('Request failed')

        try:
            return json.loads(response.text)
        except:
            return response.text

    def initialize(self, date=None):
        if not date:
            date = datetime_date.today()
        if not hasattr(settings, 'WALKING_SUGGESTION_INITIALIZATION_DAYS'):
            raise ImproperlyConfigured('No initialization days specified')
        else:
            initialization_days = settings.WALKING_SUGGESTION_INITIALIZATION_DAYS
        dates = [date - timedelta(days=offset) for offset in range(initialization_days)]
        data = {
            'totalStepsArray': [self.get_steps(date) for date in dates],
            'preStepsMatrix': [{'steps': self.get_pre_steps(date)} for date in dates],
            'postStepsMatrix': [{'steps': self.get_post_steps(date)} for date in dates]
        }
        self.make_request('initialize',
            data = data
        )
        self.__configuration.service_initialized_date = date
        self.__configuration.save()

    def update(self, date):
        if not self.is_initialized():
            raise self.NotInitialized()

        postdinner_decision = WalkingSuggestionDecision.objects.filter(
            user = self.__user,
            time__range = [
                self.__configuration.get_start_of_day(date),
                self.__configuration.get_end_of_day(date)
            ]
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
            'postStepsArray': self.get_post_steps(date),
            'availabilityArray': self.get_availabilities(date),
            'priorAntiArray': self.get_previous_messages(date),
            'lastActivityArray': self.get_received_messages(date),
            'locationArray': self.get_locations(date)
        }
        response = self.make_request('nightly',
            data = data
        )
    
    def decide(self, decision):
        if not self.is_initialized():
            raise self.NotInitialized()

        response = self.make_request('decision',
            data = {
                'studyDay': self.get_study_day(decision.time),
                'decisionTime': self.categorize_suggestion_time(decision),
                'availability': decision.available,
                'priorAnti': self.notified_since_previous_decision(decision),
                'lastActivity': self.previous_decision_was_received(decision),
                'location': self.get_location_type(decision)
            }
        )
        decision.a_it = response['send']
        decision.pi_id = response['probability']
        decision.save()

    def is_initialized(self):
        return self.__configuration.service_initialized

    def get_clicks(self, date):
        return 0

    def get_steps(self, date):
        try:
            account_user = FitbitAccountUser.objects.get(user=self.__user)
            day = FitbitDay.objects.get(
                account = account_user.account,
                date__year = date.year,
                date__month = date.month,
                date__day = date.day
            )
        except FitbitDay.DoesNotExist:
            return None
        return day.step_count

    def get_previous_messages(self, date):
        decisions = self.get_decisions_for(date)
        previous_messages = []
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            has_previous_message = self.notified_since_previous_decision(decision)
            previous_messages.append(has_previous_message)
        return previous_messages

    def get_received_messages(self, date):
        decisions = self.get_decisions_for(date)
        was_received = []
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            was_received.append(self.decision_was_received(decision))
        return was_received

    def get_availabilities(self, date):
        availabilities = []
        decisions = self.get_decisions_for(date) 
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            availabilities.append(decision.available)
        return availabilities

    def get_location_type(self, decision):
        location_context = decision.get_context()
        if Place.HOME in location_context:
            return 2
        if Place.WORK in location_context:
            return 1
        return 0

    def get_locations(self, date):
        locations = []
        decisions = self.get_decisions_for(date)
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            location_type = self.get_location_type(decision)
            locations.append(location_type)
        return locations

    def get_temperatures(self, date):
        temperatures = []
        forecast_content_type = ContentType.objects.get_for_model(WeatherForecast)
        decisions = self.get_decisions_for(date)
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            service = WalkingSuggestionDecisionService(decision)
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

        decision_query = WalkingSuggestionDecision.objects.filter(
            user=self.__user,
            test=False,
            time__range = self.get_time_range(date)
        )
        for time_category in SuggestionTime.TIMES:
            try:
                decision = decision_query.get(tags__tag=time_category)
            except WalkingSuggestionDecision.MultipleObjectsReturned:
                decision = decision_query.filter(tags__tag=time_category).first()
            except WalkingSuggestionDecision.DoesNotExist:
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
        decision = WalkingSuggestionDecision.objects.create(
            user = self.__user,
            time = time,
            a_it = False,
            pi_it = 0
        )
        decision.add_context('imputed')
        decision.add_context(time_category)

        decision_service = WalkingSuggestionDecisionService(decision)
        decision_service.update()
        return decision


    def get_steps_before(self, time):
        return self.get_steps_between(time - timedelta(minutes=30), time)

    def get_steps_after(self, time):
        return self.get_steps_between(time, time + timedelta(minutes=30))

    def get_steps_between(self, start_time, end_time):
        account_user = FitbitAccountUser.objects.get(user = self.__user)
        step_counts = FitbitMinuteStepCount.objects.filter(
            account = account_user.account,
            time__range = (start_time, end_time)
        ).all()
        total_steps = 0
        for step_count in step_counts:
            total_steps += step_count.steps
        return total_steps

    def get_study_day(self, time):
        day = datetime_date(time.year, time.month, time.day)
        initialized_day = datetime_date(
            year = self.__configuration.service_initialized_date.year,
            month = self.__configuration.service_initialized_date.month,
            day = self.__configuration.service_initialized_date.day
        )
        difference = day - self.__configuration.service_initialized_date
        return difference.days
    
    def categorize_suggestion_time(self, decision):
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
        if not decision.notification:
            return False
        try:
            message_receipt = MessageReceipt.objects.get(
                message = decision.notification,
                type = MessageReceipt.RECEIVED
            )
            return True
        except MessageReceipt.DoesNotExist:
            return False

    def get_previous_decision(self, decision):
        return WalkingSuggestionDecision.objects.filter(
            user = decision.user,
            test = False,
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
