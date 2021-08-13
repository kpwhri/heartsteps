from django.apps import AppConfig


class FeatureFlagsConfig(AppConfig):
    name = 'feature_flags'

    def ready(self):
        import feature_flags.receivers
