import django.dispatch

suggestion_times_updated = django.dispatch.Signal(providing_args=["username"])