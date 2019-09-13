from django import forms

from .models import Participant


class SendSMSForm(forms.Form):

    to_number = forms.CharField(max_length=13)
    body = forms.CharField()


class TextHistoryForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['text_message_history']

    to_number = forms.CharField(max_length=13)
    body = forms.CharField()
