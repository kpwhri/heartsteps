from celery import shared_task
from datetime import timedelta

from django.utils import timezone

from push_messages.services import PushMessageService
from surveys.serializers import SurveySerializer

from .models import Configuration
from .models import ActivitySurvey
from .models import FitbitActivity
from .services import ActivitySurveyService 

@shared_task
def randomize_activity_survey(fitbit_activity_id, username):
    try:
        configuration = Configuration.objects.get(
            user__username = username,
            enabled = True
        )
        fitbit_activity = FitbitActivity.objects.get(
            id = fitbit_activity_id
        )
    except FitbitActivity.DoesNotExist:
        return 'Fitbit activity %d does not exist' % (fitbit_activity_id)
    except Configuration.DoesNotExist:
        return 'Activity survey configuration for %s does not exist' % (username)

    hour_ago = timezone.now() - timedelta(minutes=60)
    if fitbit_activity.end_time < hour_ago:
        return 'Fitbit activity ended more than an hour ago'
    
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
