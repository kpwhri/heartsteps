from django.apps import AppConfig


class BoutPlanningNotificationConfig(AppConfig):
    name = 'bout_planning_notification'

    def ready(self):
        import bout_planning_notification.receivers
