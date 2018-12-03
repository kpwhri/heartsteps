from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = 'locations'

    def ready(self):
        import locations.receivers
