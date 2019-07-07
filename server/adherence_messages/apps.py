from django.apps import AppConfig


class AdherenceMessagesConfig(AppConfig):
    name = 'adherence_messages'

    def ready(self):
        import adherence_messages.receivers
