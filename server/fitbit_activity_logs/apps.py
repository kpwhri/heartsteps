from django.apps import AppConfig


class FitbitActivityLogsConfig(AppConfig):
    name = 'fitbit_activity_logs'

    def ready(self):
        import fitbit_activity_logs.receivers
