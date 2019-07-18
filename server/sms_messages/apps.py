from django.apps import AppConfig


class SmsMessagesConfig(AppConfig):
    name = 'sms_messages'

    def ready(self):
        import sms_messages.receivers
