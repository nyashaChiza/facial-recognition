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