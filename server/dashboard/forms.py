from django import forms
from django.core.validators import validate_slug

from participants.models import Participant, Study
from sms_messages.models import Message
from burst_periods.models import BurstPeriod
from feature_flags.models import FeatureFlags


class SendSMSForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea())


class ParticipantCreateForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['heartsteps_id', 'enrollment_token', 'birth_year']

    def clean_heartsteps_id(self):
        heartsteps_id = self.cleaned_data['heartsteps_id']
        validate_slug(heartsteps_id)
        return heartsteps_id


# TODO: make custom form fields
class FeatureFlagEditForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['studywide_feature_flags']


class ParticipantEditForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['enrollment_token', 'birth_year']


class BurstPeriodForm(forms.ModelForm):

    class Meta:
        model = BurstPeriod
        fields = ['start', 'end']


class ClockFacePairForm(forms.Form):
    pin = forms.CharField(
        required=True
    )
