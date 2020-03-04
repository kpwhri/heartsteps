from celery import shared_task

from .models import Configuration
from .models import ActivitySurvey

@shared_task
def randomize_activity_survey(fitbit_activity_id, username):
    try:
        configuration = Configuration.objects.get(
            user__username = username,
            enabled = True
        )
    except Configuration.DoesNotExist:
        return 'Activity survey configuration for %s does not exist' % (username)
    
