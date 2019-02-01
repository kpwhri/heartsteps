from random import randint
import pytz
from datetime import timedelta
from timezonefinder import TimezoneFinder

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from locations.models import Location, Place
from locations.services import LocationService
from push_messages.services import PushMessageService
from push_messages.models import Message
from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from weather.services import WeatherService
from weather.models import WeatherForecast

from randomization.models import Decision, DecisionContext, ContextTag

class DecisionService():
    def __init__(self, decision):
        self.decision = decision
        self.user = decision.user

    def create_decision(user, time = None):
        if not time:
            time = timezone.now()
        decision = Decision.objects.create(
            user = user,
            time = time
        )
        return DecisionService(decision)

    def request_context(self):
        try:
            push_message_service = PushMessageService(self.user)
        except PushMessageService.DeviceMissingError:
            return False
        message = push_message_service.send_data({
            'type': 'request-context',
            'decisionId': str(self.decision.id)
        })
        if message:
            DecisionContext.objects.create(
                decision = self.decision,
                content_object = message
            )
            return True
        else:
            return False
    
    def get_context_requests(self):
        objects = DecisionContext.objects.filter(
            decision = self.decision,
            content_type = ContentType.objects.get_for_model(Message)
        ).all()
        context_requests = []
        for obj in objects:
            message = obj.content_object
            if message.message_type == Message.DATA:
                context_requests.append(message)            
        return context_requests

    def generate_context(self):
        return []

    def add_context(self, tag_text):
        self.decision.add_context(tag_text)

    def update_context(self):
        new_context = self.generate_context()
        for tag in self.generate_context():
            self.add_context(tag)

    def update_availability(self):
        pass

    def decide(self):
        self.update_availability()
        return self.decision.decide()
    

class DecisionContextService(DecisionService):

    def generate_context(self):
        location_context = self.get_location_context()
        weather_context = self.get_weather_context()
        week_context = self.get_week_context()

        return [location_context, weather_context, week_context]

    def get_location(self):
        if hasattr(self, 'location'):
            return self.location
        location_content_type = ContentType.objects.get_for_model(Location)
        existing_decision_locations = DecisionContext.objects.filter(
            decision = self.decision,
            content_type = location_content_type
        ).all()
        if len(existing_decision_locations) > 0:
            self.location = existing_decision_locations[0].content_object
            return self.location
        try:
            location_service = LocationService(self.user)
            location = location_service.get_last_location()
            DecisionContext.objects.create(
                decision = self.decision,
                content_object = location
            )
            self.location = location
            return location
        except LocationService.UnknownLocation:
            return None
            
    def get_location_context(self):
        location = self.get_location()
        if location:
            location_service = LocationService(self.user)
            return location_service.categorize_location(
                latitude = location.latitude,
                longitude = location.longitude
            )
        else:
            return Place.OTHER

    def get_weather_context(self):
        location = self.get_location()
        if location:
            return self.get_weather_context_for_location(location)
        else:
            return self.get_imputed_weather_context()
    
    def get_weather_context_for_location(self, location):
        forecast = self.make_forecast(
            latitude = location.latitude,
            longitude = location.longitude
        )
        return WeatherService.get_forecast_context(forecast)

    def get_imputed_weather_context(self):
        forecasts = self.impute_forecasts()
        return WeatherService.get_average_forecast_context(forecasts)

    def get_forecasts(self):
        forecast_content_type = ContentType.objects.get_for_model(WeatherForecast)
        content_objects = DecisionContext.objects.filter(
            decision = self.decision,
            content_type = forecast_content_type
        ).all()
        if not len(content_objects):
            return self.create_forecasts()
        else:
            return [obj.content_object for obj in content_objects]

    def create_forecasts(self):
        location = self.get_location()
        if location:
            forecast = self.make_forecast(
                latitude = location.latitude,
                longitude = location.longitude
            )
            return [forecast]
        else:
            return self.impute_forecasts()

    def impute_forecasts(self):
        forecasts = []
        for place in Place.objects.filter(user=self.user).all():
            forecast = self.make_forecast(
                latitude = place.latitude,
                longitude = place.longitude)
            forecasts.append(forecast)
        return forecasts

    def make_forecast(self, latitude, longitude):
        forecast = WeatherService.make_forecast(
            latitude = latitude,
            longitude = longitude,
            time = self.decision.time
        )
        DecisionContext.objects.create(
            decision = self.decision,
            content_object = forecast
        )
        return forecast

    def get_local_decision_time(self):
        location = self.get_location()
        if location:
            timezone_finder = TimezoneFinder()
            timezone_string = timezone_finder.timezone_at(
                lng = location.longitude,
                lat = location.latitude
            )
            local_timezone = pytz.timezone(timezone_string)
            return self.decision.time.astimezone(local_timezone)
        return self.decision.time


    def get_week_context(self):
        WEEKEND_DAYS = [5, 6]
        local_time = self.get_local_decision_time()
        day_of_week = local_time.weekday()
        if day_of_week in WEEKEND_DAYS:
            return "weekend"
        else:
            return "weekday"

class DecisionMessageService(DecisionService):

    MESSAGE_TEMPLATE_MODEL = MessageTemplate

    def update_availability(self):
        recent_notification_count = Message.objects.filter(
            recipient = self.decision.user,
            created__range = [
                self.decision.time - timedelta(minutes=60),
                self.decision.time
            ],
            message_type = Message.NOTIFICATION
        ).count()
        if recent_notification_count > 0:
            self.decision.available = False
            self.decision.save()
        else:
            self.decision.available = True
            self.decision.save()

    def get_message_template_tags(self):
        tags = self.decision.get_context()
        if len(tags) < 1:
            return []
        message_tags_query = Q()
        for tag in tags:
            message_tags_query |= Q(tag=tag)
        return MessageTag.objects.filter(message_tags_query).all()

    def create_message_template(self):
        query = self.MESSAGE_TEMPLATE_MODEL.objects
        for tag in self.get_message_template_tags():
            query = query.filter(context_tags__in=[tag])
        message_templates = query.all()

        if len(message_templates) == 0:
            raise ValueError("No matching message template")
        if len(message_templates) == 1:
            return message_templates[0]
        return message_templates[randint(0, len(message_templates)-1)]

    def get_message_template(self):
        if hasattr(self, '__message_template'):
            return self.__message_template
        try:
            context_object = DecisionContext.objects.get(
                decision = self.decision,
                content_type = ContentType.objects.get_for_model(self.MESSAGE_TEMPLATE_MODEL)
            )
            message_template = context_object.content_object
            return message_template
        except DecisionContext.DoesNotExist:
            message_template = self.create_message_template()
            DecisionContext.objects.create(
                decision = self.decision,
                content_object = message_template
            )
            self.__message_template = message_template
            return message_template

    def send_message(self):
        push_message_service = PushMessageService(self.user)
        message_template = self.get_message_template()
        message = push_message_service.send_notification(
            message_template.body,
            title = message_template.title
            )
        DecisionContext.objects.create(
            decision = self.decision,
            content_object = message
        )
