from os import path
from celery import shared_task
from datetime import timedelta

from django.utils import timezone

from push_messages.services import PushMessageService
from surveys.serializers import SurveySerializer

from .models import Configuration
from .models import Decision
from .models import WalkingSuggestionSurvey
from .resources import WalkingSuggestionSurveyDecisionResource

@shared_task
def randomize_walking_suggestion_survey(username):
    try:
        configuration = Configuration.objects.get(
            user__username = username,
            enabled = True
        )
    except Configuration.DoesNotExist:
        return 'Walking suggestion survey configuration for %s does not exist' % (username)

    configuration.randomize_survey()

def export_walking_suggestion_surveys(username, directory='./', filename=None, start=None, end=None):
    if not filename:
        filename = '{username}.walking-suggestion-surveys.csv'.format(
            username = username
        )
    
    decision_query = Decision.objects.filter(user__username=username) \
    .prefetch_related('user') \
    .prefetch_related('notification') \
    .preload_surveys()

    if start:
        decision_query = decision_query.filter(
            created__gte=start
        )
    if end:
        decision_query = decision_query.filter(
            created__lte = end
        )
    dataset = WalkingSuggestionSurveyDecisionResource().export(decision_query.all())
    _file = open(path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
