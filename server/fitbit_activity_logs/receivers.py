from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from activity_logs.models import ActivityType, ActivityLog, ActivityLogSource
from fitbit_activities.models import FitbitActivity, FitbitActivityType
from fitbit_api.services import FitbitService
from fitbit_api.models import FitbitAccountUser

from .models import FitbitActivityToActivityType
from .services import FitbitActivityLogService

@receiver(post_save, sender=FitbitActivityType)
def map_fitbit_activity_type_to_activity_type(sender, instance, *args, **kwargs):
    fitbit_activity_type = instance
    if hasattr(fitbit_activity_type, 'account'):
        fitbit_account = fitbit_activity_type.account
        query = FitbitAccountUser.objects.filter(account=fitbit_account)
        if query.exists():
            user = query.first().user

    if fitbit_account and user:
        # try to find the user-non-specific activity type
        try:
            FitbitActivityToActivityType.objects.get(fitbit_activity_type=fitbit_activity_type, user=None)
        except FitbitActivityToActivityType.DoesNotExist:
            try:
                FitbitActivityToActivityType.objects.get(fitbit_activity_type=fitbit_activity_type, user=user)
            except FitbitActivityToActivityType.DoesNotExist:
                activity_type_name = fitbit_activity_type.name.lower().replace(' ','_')
                activity_type, _ = ActivityType.objects.get_or_create(
                    name=activity_type_name,
                    defaults= {
                        'title': fitbit_activity_type.name
                    }
                )
                FitbitActivityToActivityType.objects.create(
                    fitbit_activity_type = fitbit_activity_type,
                    activity_type = activity_type,
                    user=user
                )
    else:
        raise Exception('Activity type does not have Fitbit account or user link: {}'.format(fitbit_activity_type))

@receiver(post_save, sender=FitbitActivity)
def update_activity_log_from_fitbit_activity(sender, instance, *args, **kwargs):
    fitbit_activity = instance

    fitbit_service = FitbitService(account = fitbit_activity.account)
    for user in fitbit_service.get_users():
        if fitbit_activity.duration > 10:
            service = FitbitActivityLogService(user = user)
            try:
                activity_log = service.get_activity_log(fitbit_activity)
                service.update_activity_log(activity_log, fitbit_activity)
            except FitbitActivityLogService.NoActivityLog:
                service.create_activity_log(fitbit_activity)
