import django.dispatch

participant_enrolled = django.dispatch.Signal(providing_args=["username"])