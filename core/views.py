from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Citizen, Incident, CitizenImage
from .forms import CitizenSearchForm
from django.db import models
from .forms import CitizenSearchForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Citizen, Incident


class IndexView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CitizenSearchForm
        return context


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
    
class IncidentCreateView(CreateView):
    model = Incident
    fields = '__all__'
    context_object_name = 'incident'
    template_name = 'incidents/create.html'
    
class CitizenCreateView(CreateView):
    model = Citizen
    fields = '__all__'
    context_object_name = 'incident'
    template_name = 'citizens/create.html'    
    
class IncidentListView(ListView):
    model = Incident
    context_object_name = 'incidents'
    template_name = 'incidents/index.html'
    

class ImagesListView(ListView):
    model = CitizenImage
    context_object_name = 'images'
    template_name = 'images/index.html'
    


def search_citizens(request):
    
    citizens = []

    if request.GET:
        search_query = request.GET['search_query']
        citizens = Citizen.objects.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(id_number__icontains=search_query)
        )

    return render(request, 'citizens/search_results.html', {'citizens': citizens})


# views.py


def generate_incident_report(request, citizen_id):
    citizen = get_object_or_404(Citizen, pk=citizen_id)
    incidents = citizen.incidents.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{citizen.first_name} {citizen.last_name} Report.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Add content to the PDF
    p.drawString(100, 800, f"Incident Report for {citizen.first_name} {citizen.last_name}")

    y_position = 780
    for incident in incidents:
        y_position -= 20
        p.drawString(100, y_position, f"Title: {incident.title}")
        y_position -= 15
        p.drawString(100, y_position, f"Comment: {incident.comment}")
        y_position -= 15
        p.drawString(100, y_position, f"Created: {incident.incident_date}")
        y_position -= 15
        p.drawString(100, y_position, "--------------------------------------------")

    # Close the PDF object cleanly, and return the response.
    p.showPage()
    p.save()

    return response
