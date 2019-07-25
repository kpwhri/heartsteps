from django.dispatch import Signal

nightly_update = Signal(providing_args=['day', 'user'])
