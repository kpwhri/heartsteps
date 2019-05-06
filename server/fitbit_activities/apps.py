from django.apps import AppConfig


class FitbitActivitiesConfig(AppConfig):
    name = 'fitbit_activities'

    def ready(self):
        import fitbit_activities.receivers
