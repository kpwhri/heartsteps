from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from activity_logs.models import ActivityLog, ActivityLogSource
from fitbit_activities.models import FitbitActivity

from fitbit_api.services import FitbitService

from .models import FitbitActivityToActivityType

User = get_user_model()

class FitbitActivityLogService(FitbitService):

    class NoActivityLog(ActivityLogSource.DoesNotExist):
        pass

    def __init__(self, user=None, username=None):
        if username:
            user = User.objects.get(username=username)
        super().__init__(user=user)
        self.__user = user

    def get_activity_log(self, fitbit_activity):
        activity_log_source = self.get_activity_log_source(fitbit_activity)
        return activity_log_source.activity_log
        
    def get_activity_log_source(self, fitbit_activity):
        try:
            activity_log_source = ActivityLogSource.objects.get(
                content_type = ContentType.objects.get_for_model(FitbitActivity),
                object_id = fitbit_activity.id,
                user = self.__user
            )
            return activity_log_source
        except ActivityLogSource.DoesNotExist:
            raise FitbitActivityLogService.NoActivityLog('No matching activity log')    
    
    def create_activity_log(self, fitbit_activity):
        activity_log = ActivityLog.objects.create(
            user = self.__user,
            type = self.get_matching_activity_type(fitbit_activity.type),
            start = fitbit_activity.start_time,
            duration = fitbit_activity.duration
        )
        ActivityLogSource.objects.create(
            activity_log = activity_log,
            content_object = fitbit_activity,
            updated_at = activity_log.updated_at,
            user = self.__user
        ) 
        return activity_log

    def update_activity_log(self, activity_log, fitbit_activity):
        activity_log_source = self.get_activity_log_source(fitbit_activity)
        if activity_log_source.can_update:
            activity_log = activity_log_source.activity_log
            activity_log.type = self.get_matching_activity_type(fitbit_activity.type)
            activity_log.start = fitbit_activity.start_time
            activity_log.duration = fitbit_activity.duration
            activity_log.save()
            activity_log_source.updated_at = activity_log.updated_at
            activity_log_source.save()

    def get_matching_activity_type(self, fitbit_activity_type):
        connection = FitbitActivityToActivityType.objects.get(fitbit_activity_type=fitbit_activity_type)
        return connection.activity_type




