import django.dispatch

step_count_updated = django.dispatch.Signal(providing_args=["username"])
