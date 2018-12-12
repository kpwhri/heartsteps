from django.apps import AppConfig


class WalkingSuggestionsConfig(AppConfig):
    name = 'walking_suggestions'

    def ready(self):
        import walking_suggestions.receivers