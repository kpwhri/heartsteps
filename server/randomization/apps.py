from django.apps import AppConfig


class RandomizationAppConfig(AppConfig):
    name = 'randomization'

    def ready(self):
        import randomization.receivers
