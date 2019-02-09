from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes.models import ContentType

from activity_logs.models import ActivityType, ActivityLog, ActivityLogSource
from fitbit_api.models import FitbitActivity, FitbitActivityType
from fitbit_api.services import FitbitService

from .models import FitbitActivityToActivityType

@receiver(post_save, sender=FitbitActivityType)
def map_fitbit_activity_type_to_activity_type(sender, instance, *args, **kwargs):
    fitbit_activity_type = instance
    try:
        FitbitActivityToActivityType.objects.get(fitbit_activity=fitbit_activity_type)
    except FitbitActivityToActivityType.DoesNotExist:
        activity_type_name = fitbit_activity_type.name.lower()
        activity_type, _ = ActivityType.objects.get_or_create(
            name=activity_type_name,
            defaults= {
                'title': fitbit_activity_type.name
            }
        )
        FitbitActivityToActivityType.objects.create(
            fitbit_activity = fitbit_activity_type,
            activity_type = activity_type
        )

@receiver(post_save, sender=FitbitActivity)
def update_activity_log_from_fitbit_activity(sender, instance, *args, **kwargs):
    fitbit_activity = instance

    connection = FitbitActivityToActivityType.objects.get(fitbit_activity=fitbit_activity.type)
    activity_type = connection.activity_type
    
    fitbit_service = FitbitService(account = fitbit_activity.account)
    for user in fitbit_service.get_users():
        try:
            activity_log_source = ActivityLogSource.objects.get(
                content_type = ContentType.objects.get_for_model(FitbitActivity),
                object_id = fitbit_activity.id
            )
            if activity_log_source.can_update:
                activity_log = activity_log_source.activity_log
                activity_log.type = activity_type
                activity_log.start = fitbit_activity.start_time
                activity_log.duration = fitbit_activity.duration
                activity_log.save()
                activity_log_source.updated_at = activity_log.updated_at
        except ActivityLogSource.DoesNotExist:
            activity_log = ActivityLog.objects.create(
                user = user,
                type = activity_type,
                start = fitbit_activity.start_time,
                duration = fitbit_activity.duration
            )
            ActivityLogSource.objects.create(
                activity_log = activity_log,
                content_object = fitbit_activity,
                updated_at = activity_log.updated_at
            )
