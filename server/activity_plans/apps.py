from django.apps import AppConfig


class ActivityPlansConfig(AppConfig):
    name = 'activity_plans'

    def ready(self):
        import activity_plans.receivers
