from django.apps import AppConfig


class WeeklyReflectionConfig(AppConfig):
    name = 'weekly_reflection'

    def ready(self):
        import weekly_reflection.receivers
