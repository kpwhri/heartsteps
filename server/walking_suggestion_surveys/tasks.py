from celery import shared_task
from datetime import timedelta

from django.utils import timezone

from push_messages.services import PushMessageService
from surveys.serializers import SurveySerializer

from .models import Configuration
from .models import WalkingSuggestionSurvey

@shared_task
def randomize_walking_suggestion_survey(username):
    try:
        configuration = Configuration.objects.get(
            user__username = username,
            enabled = True
        )
    except Configuration.DoesNotExist:
        return 'Walking suggestion survey configuration for %s does not exist' % (username)

    survey = configuration.randomize_survey()
    if survey:
        survey.send_notification()
