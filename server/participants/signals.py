from django.dispatch import Signal

initialize_participant = Signal(providing_args=['user'])

nightly_update = Signal(providing_args=['day', 'user'])
