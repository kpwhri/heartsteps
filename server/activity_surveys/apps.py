from django.apps import AppConfig


class ActivitySurveysConfig(AppConfig):
    name = 'activity_surveys'

    def ready(self):
        import activity_surveys.receivers
