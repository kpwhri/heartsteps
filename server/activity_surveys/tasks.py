from os import path
from celery import shared_task

from push_messages.services import PushMessageService
from surveys.serializers import SurveySerializer

from .models import Configuration
from .models import ActivitySurvey
from .models import FitbitActivity
from .models import Decision
from .resources import ActivitySurveyDecisionResource
from .services import ActivitySurveyService 

@shared_task
def randomize_activity_survey(fitbit_activity_id, username):
    try:
        configuration = Configuration.objects.get(
            user__username = username
        )
        fitbit_activity = FitbitActivity.objects.get(
            id = fitbit_activity_id
        )
    except FitbitActivity.DoesNotExist:
        return 'Fitbit activity %d does not exist' % (fitbit_activity_id)
    except Configuration.DoesNotExist:
        return 'Activity survey configuration for %s does not exist' % (username)
    
    existing_activity_survey_count = ActivitySurvey.objects.filter(
        user = configuration.user,
        fitbit_activity = fitbit_activity
    )
    if existing_activity_survey_count:
        return 'Activity survey already created for fitbit activity %d' % (fitbit_activity.id)
    else:
        service = ActivitySurveyService(configuration = configuration)
        service.randomize_survey(
            fitbit_activity = fitbit_activity
        )
        return 'Randomized activity survey'

def export_activity_surveys(username, directory='./', filename=None, start=None, end=None):
    if not filename:
        filename = '{username}.activity_surveys.csv'.format(
            username = username
        )
    decision_query = Decision.objects.filter(
        user__username = username
    ) \
    .preload_activity_surveys() \
    .prefetch_related('user') \
    .prefetch_related('notification') \
    .prefetch_related('fitbit_activity')

    if start:
        decision_query = decision_query.filter(
            created__gte = start
        )
    if end:
        decision_query = decision_query.filter(
            created__lte = end
        )

    dataset = ActivitySurveyDecisionResource().export(decision_query.all())
    _file = open(path.join(directory, filename), 'w')
    _file.write(dataset.csv)
    _file.close()
