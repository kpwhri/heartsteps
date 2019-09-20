from django import forms

from sms_messages.models import Message


class SendSMSForm(forms.Form):

    to_number = forms.CharField(max_length=13)
    body = forms.CharField()


class TextHistoryForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body', ]
        readonly_fields = ['created', ]
