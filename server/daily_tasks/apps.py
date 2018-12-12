from django.apps import AppConfig


class DailyTasksConfig(AppConfig):
    name = 'daily_tasks'

    def ready(self):
        import daily_tasks.receivers