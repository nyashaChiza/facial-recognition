# forms.py (inside your app)

import re

from django import forms
from .models import Citizen, Incident, CitizenImage, Config

VEHICLE_REG_PATTERN = re.compile(r'^[A-Za-z0-9\- ]+$')


class CitizenForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CitizenForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Citizen
        fields = '__all__'
        exclude = ('picture', 'is_blacklisted', 'blacklist_reason')


class CitizenSearchForm(forms.Form):
    search_query = forms.CharField(
        label='Search',
        widget=forms.TextInput(attrs={'class': 'form-control bg-white border-0 px-1'})
    )


class BlacklistForm(forms.ModelForm):
    class Meta:
        model = Citizen
        fields = ('is_blacklisted', 'blacklist_reason')
        widgets = {
            'is_blacklisted': forms.HiddenInput(),  # Hide the is_blacklisted field
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['is_blacklisted'].initial = True

    def clean_blacklist_reason(self):
        reason = (self.cleaned_data.get('blacklist_reason') or '').strip()
        if not reason:
            raise forms.ValidationError('Please provide a reason for blacklisting this driver.')
        return reason


class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = ('minimum_detection_threshold', 'maximum_detection_threshold', 'maximum_points_threshold')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class IncidentForm(forms.ModelForm):
    image_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(IncidentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Incident
        fields = ['title', 'vehicle_registration_number', 'points', 'location', 'comment', 'incident_date', 'image_data']
        widgets = {
            'incident_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_vehicle_registration_number(self):
        value = (self.cleaned_data.get('vehicle_registration_number') or '').strip()
        if value and not VEHICLE_REG_PATTERN.match(value):
            raise forms.ValidationError(
                'Vehicle registration number may only contain letters, numbers, spaces, and hyphens.'
            )
        return value


class CitizenImageForm(forms.ModelForm):
    class Meta:
        model = CitizenImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'capture': 'camera'}),
        }
