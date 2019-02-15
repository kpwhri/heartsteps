from django.apps import AppConfig


class AntiSedentaryConfig(AppConfig):
    name = 'anti_sedentary'

    def ready(self):
        import anti_sedentary.receivers
