from django import forms

from participants.models import Participant
from sms_messages.models import Message

class SendSMSForm(forms.Form):

    to_number = forms.CharField(max_length=13)
    body = forms.CharField(widget=forms.Textarea())

class TextHistoryForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body', ]
        readonly_fields = ['created', ]

class ParticipantCreateForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['heartsteps_id', 'enrollment_token', 'birth_year']

class ParticipantEditForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['enrollment_token', 'birth_year']

