from django.dispatch import Signal

initialize_participant = Signal(providing_args=['participant'])

nightly_update = Signal(providing_args=['day', 'user'])
