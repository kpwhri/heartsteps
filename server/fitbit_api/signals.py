import django.dispatch

update_date = django.dispatch.Signal(providing_args=["fitbit_user", "date"])