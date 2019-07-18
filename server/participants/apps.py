from django.apps import AppConfig

class ParticipantsConfig(AppConfig):
    name = 'participants'

    def ready(self):
        import participants.receivers
