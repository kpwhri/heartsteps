from django.apps import AppConfig


class MorningMessagesConfig(AppConfig):
    name = 'morning_messages'

    def ready(self):
        import morning_messages.receivers
