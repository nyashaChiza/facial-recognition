# forms.py (inside your app)

from django import forms
from .models import Citizen

class CitizenForm(forms.ModelForm):
    class Meta:
        model = Citizen
        fields = '__all__'



class CitizenSearchForm(forms.Form):
    search_query = forms.CharField(
        label='Search',
        widget=forms.TextInput(attrs={'class': 'form-control bg-white border-0 px-1'})
    )
    
from django import forms
from .models import Citizen, Incident, CitizenImage

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'comment', 'incident_date']

# class CitizenForm(forms.ModelForm):
#     class Meta:
#         model = Citizen
#         fields = ['first_name', 'last_name', 'id_type', 'id_number']

class CitizenImageForm(forms.ModelForm):
    class Meta:
        model = CitizenImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'capture': 'camera'}),
        }
