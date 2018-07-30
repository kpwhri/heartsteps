# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.contrib.auth.models import User
from heartsteps_locations.models import determine_user_location_type
from .models import Decision


@shared_task
def make_decision(decision_id):
    decision = Decision.objects.get(id=decision_id)
    
    if not hasattr(decision, 'location'):
        decision.get_context()
        return

    location_type = determine_user_location_type(
        user = decision.user,
        latitude = decision.location.lat,
        longitude = decision.location.long
    )
    decision.add_context(location_type)

    if decision.decide():
        decision.make_message()
        decision.send_message()