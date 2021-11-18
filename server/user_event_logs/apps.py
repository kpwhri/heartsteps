from django.apps import AppConfig


class UserEventLogsConfig(AppConfig):
    name = 'user_event_logs'

    def ready(self):
        from . import signals
