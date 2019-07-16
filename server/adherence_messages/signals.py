from django.dispatch import Signal

send_adherence_message = Signal(providing_args=['adherence_alert'])

update_adherence = Signal(providing_args=['user', 'date'])
