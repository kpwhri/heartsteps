from django.apps import AppConfig


class HeartstepsMessagesConfig(AppConfig):
    name = 'heartsteps_messages'

    def ready(self):
        import heartsteps_messages.receivers
