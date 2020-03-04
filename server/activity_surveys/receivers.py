from django.db.models.signals import post_save

from fitbit_activities.models import FitbitActivity

from .models import Configuration
from .tasks import randomize_activity_survey

def randomize_fitbit_activity_survey_reveiver(sender, instance, created, *args, **kwargs):
    if not created:
        return
    fitbit_activity = instance
    users = fitbit_activity.account.get_users()

    for user in fitbit_activity.account.get_users():
        try:
            config = Configuration.objects.get(
                user = user,
                enabled = True
            )
            randomize_activity_survey.apply_async(
                kwargs = {
                    'fitbit_activity_id': fitbit_activity.id,
                    'username': user.username
                }
            )
        except Configuration.DoesNotExist:
            continue

post_save.connect(randomize_fitbit_activity_survey_reveiver, sender=FitbitActivity)
