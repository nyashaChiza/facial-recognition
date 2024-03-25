# forms.py (inside your app)

from django import forms
from .models import Citizen, Incident, CitizenImage

class CitizenForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CitizenForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Citizen
        fields = '__all__'
        exclude = ('picture','is_blacklisted', 'blacklist_reason')


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['is_blacklisted'].initial = True
    


class IncidentForm(forms.ModelForm):
    image_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(IncidentForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Incident
        fields = ['title','vehicle_registration_number','location', 'comment', 'incident_date', 'image_data']
        widgets = {
            'incident_date': forms.DateInput(attrs={'type': 'date'})
        }




class CitizenImageForm(forms.ModelForm):
    class Meta:
        model = CitizenImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'capture': 'camera'}),
        }
