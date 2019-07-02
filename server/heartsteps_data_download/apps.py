from django.apps import AppConfig


class HeartstepsDataDownloadConfig(AppConfig):
    name = 'heartsteps_data_download'

    def ready(self):
        import heartsteps_data_download.receivers
