import django.dispatch

weekly_reflection = django.dispatch.Signal(providing_args=["username"])