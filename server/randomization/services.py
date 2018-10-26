from random import randint
import pytz
from timezonefinder import TimezoneFinder

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from locations.models import Location, Place
from locations.factories import get_last_user_location, determine_location_type
from locations.models import OTHER as LOCATION_TYPE_OTHER
from push_messages.services import PushMessageService
from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from weather.services import WeatherService

from randomization.models import Decision, DecisionContext, Message, ContextTag

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
            'type': 'get_context'
        })
        if message:
            return True
        else:
            return False

    def generate_context(self):
        return []

    def add_context(self, tag_text):
        tag, created = ContextTag.objects.get_or_create(
            tag = tag_text
        )
        self.decision.tags.add(tag)

    def update_context(self):
        new_context = self.generate_context()
        for tag in self.generate_context():
            self.add_context(tag)
    

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
        location = get_last_user_location(self.user)
        if location:
            DecisionContext.objects.create(
                decision = self.decision,
                content_object = location
            )
            self.location = location
            return location
        return None
            
    def get_location_context(self):
        location = self.get_location()
        if location:
            location_type = determine_location_type(
                user = self.user,
                latitude = location.latitude,
                longitude = location.longitude
            )
            return location_type
        else:
            return LOCATION_TYPE_OTHER

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
        forecasts = []
        for place in Place.objects.filter(user=self.user).all():
            forecast = self.make_forecast(
                latitude = place.latitude,
                longitude = place.longitude
            )
            forecasts.append(forecast)
        return WeatherService.get_average_forecast_context(forecasts)

    def make_forecast(self, latitude, longitude):
        forecast = WeatherService.make_forecast(
            latitude = latitude,
            longitude = longitude
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

    def create_message(self):
        message = Message(
            decision = self.decision
        )
        message_template = self.get_message_template()
        if not message_template:
            raise ValueError("No matching message template")
        message.message_template = message_template
        message.save()
        self.message = message
        return message

    def get_message_template_tags(self):
        message_tags_query = Q()
        for tag in self.decision.tags.all():
            message_tags_query |= Q(tag=tag.tag)
        return MessageTag.objects.filter(message_tags_query).all()

    def get_message_template(self):
        query = MessageTemplate.objects
        for tag in self.get_message_template_tags():
            query = query.filter(context_tags__in=[tag])
        message_templates = query.all()

        if len(message_templates) == 0:
            return False
        if len(message_templates) == 1:
            return message_templates[0]
        return message_templates[randint(0, len(message_templates)-1)]

    def send_message(self):
        try:
            push_message_service = PushMessageService(self.user)
        except PushMessageService.DeviceMissingError:
            return False
        message = push_message_service.send_notification(
            self.message.message_template.body,
            title = self.message.message_template.title
            )
        if message:
            self.message.sent_message = message
            self.message.save()
            return True
        return False