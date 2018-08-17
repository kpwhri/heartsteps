# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from weather.functions import WeatherFunction
from locations.factories import get_last_user_location

from django.contrib.auth.models import User
from locations.models import Location, determine_place_type
from .models import Decision


@shared_task
def make_decision(decision_id):
    decision = Decision.objects.get(id=decision_id)
    if decision.is_complete():
        return False

    location = get_last_user_location(decision.user)
    if location:
        location_type = determine_place_type(
            user = decision.user,
            latitude = location.latitude,
            longitude = location.longitude
        )
        decision.add_context(location_type)

        forecast, weather_context = WeatherFunction.get_context(
            latitude = location.latitude,
            longitude = location.longitude
        )
        decision.add_context(weather_context)
    else:
        decision.add_context("location unknown")

    if decision.decide():
        decision.make_message()
        decision.send_message()