import requests
import json
import pytz
import time
from datetime import datetime, timedelta, date as datetime_date
from urllib.parse import urljoin

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType

from anti_sedentary.models import AntiSedentaryDecision
from days.services import DayService
from fitbit_api.models import FitbitAccountUser
from fitbit_api.services import FitbitService
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from locations.models import Place
from page_views.models import PageView
from push_messages.models import MessageReceipt, Message
from randomization.models import DecisionContext
from randomization.services import DecisionService, DecisionContextService, DecisionMessageService
from weather.models import WeatherForecast
from watch_app.models import StepCount as WatchStepCount

from .models import Configuration
from .models import NightlyUpdate
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
            
            suggestion_time_today_utc = suggestion_time_today.astimezone(pytz.UTC)
            time_utc = time.astimezone(pytz.UTC)
            if time_utc < suggestion_time_today_utc:
                continue
            difference = time_utc - suggestion_time_today_utc
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

    class RandomizationUnavailable(RuntimeError):
        pass

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

    def make_decision_now(user=None, username=None):
        WalkingSuggestionDecisionService.make_decision(
            datetime = timezone.now(),
            user = user,
            username = username
        )

    def make_decision(datetime, user=None, username=None):
        category = None
        try:
            service = WalkingSuggestionTimeService(
                user = user,
                username = username
            )
            category = service.suggestion_time_category_available_at(datetime)
        except WalkingSuggestionTimeService.Unavailable:
            pass
        if not category:
            raise WalkingSuggestionDecisionService.RandomizationUnavailable('Unable to randomize at time')
        decision = service.create_decision(
            category = category,
            time = datetime
        )
        WalkingSuggestionDecisionService.process_decision(decision)

    def process_decision(decision):
        decision_service = WalkingSuggestionDecisionService(decision)
        decision_service.update_context()
        decision_service.update_availability()
        if decision_service.decide():
            decision_service.send_message()

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
        super().update_availability()

        if not self.enabled:
            self.decision.add_unavailable_reason(self.decision.UNAVAILABLE_DISABLED)
            self.decision.save()

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
            self.unavailable_disabled = True
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
            self.decision.add_unavailable_reason(self.decision.UNAVAILABLE_SERVICE_ERROR)
            self.decision.save()
        return self.decision.treated

class WalkingSuggestionService():
    """
    Handles state and requests between walking-suggestion-service and
    heartsteps-server for a specific participant.
    """

    class Unavailable(ImproperlyConfigured):
        pass

    class NotInitialized(ImproperlyConfigured):
        pass

    class UnableToInitialize(ImproperlyConfigured):
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

    def nightly_update(self, date):
        if not self.is_initialized():
            NightlyUpdate.objects.filter(user = self.__user).delete()
            self.initialize(date=date)
        else:
            last_update_query = NightlyUpdate.objects.filter(
                user = self.__user,
                updated = True,
                day__gt = self.__configuration.service_initialized_date
            )
            if last_update_query.count() > 0:
                last_updated_day = last_update_query.last().day
            else:
                last_updated_day = self.__configuration.service_initialized_date
            last_updated_day = last_updated_day + timedelta(days=1)
            while last_updated_day <= date:
                self.update(date=last_updated_day)
                NightlyUpdate.objects.update_or_create(
                    user = self.__user,
                    day = last_updated_day,
                    defaults = {
                        'updated': True
                    }
                )
                last_updated_day = last_updated_day + timedelta(days=1)

    def make_request(self, uri, data, attempt=1):
        url = urljoin(self.__base_url, uri)
        data['userID'] = self.__user.username
        request_record = ServiceRequest.objects.create(
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
            if attempt <= 2:
                attempt += 1
                time.sleep(20)
                return self.make_request(uri, data, attempt)
            raise self.RequestError('Request failed')

        try:
            return json.loads(response.text)
        except:
            return response.text

    def get_fitbit_days_before_date(self, date):
        fitbit_service = FitbitService(user = self.__user)
        return FitbitDay.objects.filter(
            account = fitbit_service.account,
            date__range = [
                self.__user.date_joined,
                date
            ]
        ).order_by('-date').all()

    def get_initialization_days(self, date):
        if not hasattr(settings, 'WALKING_SUGGESTION_INITIALIZATION_DAYS'):
            raise ImproperlyConfigured('No initialization days specified')
        initialization_days = settings.WALKING_SUGGESTION_INITIALIZATION_DAYS

        fitbit_days_worn = []
        for fitbit_day in self.get_fitbit_days_before_date(date):
            if fitbit_day.wore_fitbit and len(fitbit_days_worn) < initialization_days:
                fitbit_days_worn.append(fitbit_day.date)
        if len(fitbit_days_worn) < initialization_days:
            raise WalkingSuggestionService.UnableToInitialize('Unable to initialize participant')
        first_day_worn = fitbit_days_worn[-1]
        dates = [first_day_worn + timedelta(days=offset) for offset in range((date-first_day_worn).days)]
        dates.append(date)
        return dates

    def get_gap_days(self, dates):
        if not hasattr(settings, 'WALKING_SUGGESTION_INITIALIZATION_DAYS'):
            raise ImproperlyConfigured('No initialization days specified')
        initialization_days = settings.WALKING_SUGGESTION_INITIALIZATION_DAYS
        
        gap_dates_length = len(dates) - initialization_days + 1

        return [dates[len(dates)-offset-1] for offset in range(gap_dates_length)]

    def initialize(self, date=None):
        if not date:
            day_service = DayService(user=self.__user)
            date = day_service.get_current_date()
        dates = self.get_initialization_days(date)
        gap_dates = self.get_gap_days(dates)
        data = {
            'date': date.strftime('%Y-%m-%d'),
            'pooling': self.__configuration.pooling,
            'totalStepsArray': [self.get_steps(date) for date in dates],
            'preStepsMatrix': [{'steps': self.get_pre_steps(date)} for date in dates],
            'postStepsMatrix': [{'steps': self.get_post_steps(date)} for date in dates],
            'PriorAntiMatrix': [{'priorAnti': self.get_all_anti_sedentary_treatments(date)} for date in gap_dates],
            'DelieverMatrix': [{'walking': self.get_received_messages(date)} for date in gap_dates]
        }
        self.make_request('initialize',
            data = data
        )
        self.__configuration.service_initialized_date = date
        self.__configuration.save()

    def update(self, date):
        if not self.is_initialized():
            raise self.NotInitialized()

        data = {
            'date': date.strftime('%Y-%m-%d'),
            'studyDay': self.get_study_day(date),
            'appClick': self.get_clicks(date),
            'totalSteps': self.get_steps(date),
            'lastActivity': self.decision_category_was_received(date, SuggestionTime.POSTDINNER),
            'temperatureArray': self.get_temperatures(date),
            'preStepsArray': self.get_pre_steps(date),
            'postStepsArray': self.get_post_steps(date),
            'availabilityArray': self.get_availabilities(date),
            'priorAntiArray': self.get_all_anti_sedentary_treatments(date),
            'lastActivityArray': self.offset_received_messages(date),
            'locationArray': self.get_locations(date),
            'actionArray': self.get_actions(date),
            'probArray': self.get_probabilities(date)
        }
        response = self.make_request('nightly',
            data = data
        )
    
    def decide(self, decision):
        if not self.is_initialized():
            raise self.NotInitialized()

        day_service = DayService(user = decision.user)
        date = day_service.get_date_at(decision.time)

        response = self.make_request('decision',
            data = {
                'date': date.strftime('%Y-%m-%d'),
                'studyDay': self.get_study_day(decision.time),
                'decisionTime': self.categorize_suggestion_time(decision),
                'availability': decision.available,
                'priorAnti': self.anti_sedentary_treated_since_previous_decision(decision),
                'lastActivity': self.previous_decision_was_received(decision),
                'location': self.get_location_type(decision)
            }
        )
        decision.treated = response['send']
        decision.treatment_probability = response['probability']
        decision.save()

    def is_initialized(self):
        return self.__configuration.service_initialized

    def get_clicks(self, date):
        return PageView.objects.filter(
            user = self.__user,
            time__gte = self.__configuration.get_start_of_day(date),
            time__lte = self.__configuration.get_end_of_day(date)
        ).count()

    def get_actions(self, date):
        actions_list = []
        for decision in self.get_decision_list_for(date):
            if decision.imputed:
                actions_list.append(False)
            else:
                actions_list.append(decision.treated)
        return actions_list

    def get_probabilities(self, date):
        probability_list = []
        for decision in self.get_decision_list_for(date):
            if decision.imputed:
                probability_list.append(0)
            else:
                probability_list.append(decision.treatment_probability)
        return probability_list

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
        if day.wore_fitbit:
            return day.step_count
        return None

    def get_received_messages(self, date):
        decisions = self.get_decisions_for(date)
        was_received = []
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            was_received.append(self.decision_was_received(decision))
        return was_received

    def offset_received_messages(self, date):
        received_messages = self.get_received_messages(date)
        return [False] + received_messages[:4]

    def get_availabilities(self, date):
        availabilities = []
        decisions = self.get_decisions_for(date) 
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            if decision.available:
                availabilities.append(True)
            else:
                availabilities.append(False)
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
            if not forecast_temperatures:
                temperatures.append(None)
            else:
                average_temperature = sum(forecast_temperatures)/len(forecast_temperatures)
                temperature_celcius = (average_temperature - 32)/1.8
                temperature_celcius = round(temperature_celcius, 2)
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

    def get_decision_list_for(self, date):
        decisions = self.get_decisions_for(date)
        decisions_list = []
        for category in SuggestionTime.TIMES:
            decisions_list.append(decisions[category])
        return decisions_list

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
            treated = False,
            treatment_probability = 0,
            imputed = True
        )
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
        if total_steps > 0:
            return total_steps
        heart_rate_count = FitbitMinuteHeartRate.objects.filter(
            account = account_user.account,
            time__range = [start_time, end_time]
        ).count()
        if heart_rate_count > 0:
            return 0
        return None

    def get_study_day(self, time):
        day_service = DayService(user = self.__user)
        day = day_service.get_date_at(time)
        initialized_day = day_service.get_date_at(self.__configuration.service_initialized_date)
        difference = day - initialized_day
        return difference.days
    
    def categorize_suggestion_time(self, decision):
        for tag in decision.get_context():
            if tag in SuggestionTime.TIMES:
                return SuggestionTime.TIMES.index(tag) + 1
        raise ValueError('Decision does not have suggestion time')

    def previous_decision_was_received(self, decision):
        previous_decision = self.get_previous_decision(decision)
        return self.decision_was_received(previous_decision)

    def decision_category_was_received(self, date, category):
        decision = WalkingSuggestionDecision.objects.filter(
            user = self.__user,
            time__range = [
                self.__configuration.get_start_of_day(date),
                self.__configuration.get_end_of_day(date)
            ]
        ).filter(
            tags__tag = category
        ).first()
        if decision:
            return self.decision_was_received(decision)
        else:
            return False

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

    def anti_sedentary_treated_between(self, start, end):
        treated_anti_sedentary_decisions = AntiSedentaryDecision.objects.filter(
            user = self.__user,
            treated = True,
            time__range = [start, end]
        ).all()
        for decision in treated_anti_sedentary_decisions:
            notification = decision.notification
            if notification and notification.received:
                return True
        return False

    def anti_sedentary_treated_since_previous_decision(self, decision):
        previous_decision = self.get_previous_decision(decision)
        if previous_decision:
            start_time = previous_decision.time
        else:
            start_time = self.__configuration.get_start_of_day(decision.time)
        return self.anti_sedentary_treated_between(
            start_time,
            decision.time
        )

    def get_previous_anti_sedentary_treatments(self, date):
        decisions = self.get_decisions_for(date)
        previous_treatments = []
        for time_category in SuggestionTime.TIMES:
            decision = decisions[time_category]
            previous_treatment = self.anti_sedentary_treated_since_previous_decision(decision)
            previous_treatments.append(previous_treatment)
        return previous_treatments

    def get_end_of_day_anti_sedentary_treatment(self, date):
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
            return self.anti_sedentary_treated_between(
                postdinner_decision.time,
                self.__configuration.get_end_of_day(date)
            )
        else:
            return False

    def get_all_anti_sedentary_treatments(self, date):
        treatments = self.get_previous_anti_sedentary_treatments(date)
        treatments.append(self.get_end_of_day_anti_sedentary_treatment(date))
        return treatments
