from django.apps import AppConfig


class WalkingSuggestionSurveysConfig(AppConfig):
    name = 'walking_suggestion_surveys'

    def ready(self):
        import walking_suggestion_surveys.receivers