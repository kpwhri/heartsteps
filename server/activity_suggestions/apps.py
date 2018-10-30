from django.apps import AppConfig


class ActivitySuggestionsConfig(AppConfig):
    name = 'activity_suggestions'

    def ready(self):
        import activity_suggestions.receivers
