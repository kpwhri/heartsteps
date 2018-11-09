import django.dispatch

timezone_updated = django.dispatch.Signal(providing_args=["username"])