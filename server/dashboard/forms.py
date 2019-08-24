from django import forms

class SendSMSForm(forms.Form):

    to_number = forms.CharField(max_length=13)
    body = forms.CharField()
