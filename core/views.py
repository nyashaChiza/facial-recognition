from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Citizen, Incident, CitizenImage


class IndexView(TemplateView):
    template_name = 'home.html'


class CitizenListView(ListView):
    model = Citizen
    context_object_name = 'citizens'
    template_name = 'citizens/index.html'
    
    
class CitizenDetailView(DetailView):
    model = Citizen
    context_object_name = 'citizen'
    template_name = 'citizens/detail.html'
    
class IncidentDetailView(DetailView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incidents/detail.html'
    
class IncidentListView(ListView):
    model = Incident
    context_object_name = 'incidents'
    template_name = 'incidents/index.html'
    

class ImagesListView(ListView):
    model = CitizenImage
    context_object_name = 'images'
    template_name = 'images/index.html'