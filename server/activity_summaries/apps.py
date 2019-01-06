from django.apps import AppConfig


class ActivitySummariesConfig(AppConfig):
    name = 'activity_summaries'

    def ready(self):
        import activity_summaries.receivers