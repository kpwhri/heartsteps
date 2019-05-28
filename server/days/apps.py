from django.apps import AppConfig


class DaysConfig(AppConfig):
    name = 'days'

    def ready(self):
        import days.receivers
