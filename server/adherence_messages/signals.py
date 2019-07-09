from django.dispatch import Signal

update_adherence = Signal(providing_args=['user', 'date'])
