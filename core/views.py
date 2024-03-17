import cv2
import base64
import numpy as np
import os
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings

from reportlab.pdfgen import canvas

from .models import Citizen, Incident, CitizenImage
from .forms import CitizenSearchForm, CitizenForm, IncidentForm, CitizenImageForm
from main import FaceRecognition
from core.helpers import compare_faces

class IndexView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CitizenSearchForm()
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
    form_class = IncidentForm
    template_name = 'incidents/create.html'
    
class CitizenCreateView(CreateView):
    model = Citizen
    form_class = CitizenForm
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
    search_query = request.GET.get('search_query', '')
    citizens = []
    if search_query:
        citizens = Citizen.objects.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(id_number__icontains=search_query)
        )
    return render(request, 'citizens/search_results.html', {'citizens': citizens})

def generate_incident_report(request, citizen_id):
    citizen = get_object_or_404(Citizen, pk=citizen_id)
    incidents = citizen.incidents.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{citizen.first_name} {citizen.last_name} Report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Incident Report for {citizen.first_name} {citizen.last_name}")

    y_position = 780
    for incident in incidents:
        y_position -= 20
        p.drawString(100, y_position, f"Title: {incident.title}")
        y_position -= 15
        p.drawString(100, y_position, f"Loaction: {incident.location}")
        y_position -= 15
        p.drawString(100, y_position, f"Comment: {incident.comment}")
        y_position -= 15
        p.drawString(100, y_position, f"Created: {incident.incident_date}")
        y_position -= 15
        p.drawString(100, y_position, "--------------------------------------------")

    p.showPage()
    p.save()

    return response



def capture_driver(request):
    if request.method == 'POST':
        citizen_form = CitizenForm(request.POST)
        if citizen_form.is_valid():
            citizen = citizen_form.save(commit=False)
            image_data = request.POST.get('image_data')
            if image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                citizen.picture.save(f'citizen_{citizen}.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
            citizen.save()
            messages.success(request, 'Driver added successfully')
        else:
            messages.warning(request, 'Invalid Driver Information')
    else:
        messages.warning(request, 'Method Not Allowed')
        
    return redirect(reverse('citizen-list'))

def capture_incident(request):
    if request.method == 'POST':
        format, imgstr = request.POST.get('image_data').split(';base64,')
        ext = format.split('/')[-1]
        image_content = ContentFile(base64.b64decode(imgstr))
        temp_image_name = 'temp_image.' + ext
        with open(temp_image_name, 'wb') as f:
            f.write(image_content.read())
        driver = compare_faces(temp_image_name)
        if driver:
            incident_form = IncidentForm(request.POST)
            if incident_form.is_valid():
                incident = incident_form.save(commit=False)
                incident.citizen = driver
                incident.save()
                os.remove(temp_image_name)
                messages.success(request, f'Incident for {driver} saved successfully')
                
            else:
                messages.warning(request, f'Invalid Driver Information for {driver}')
        else:
            os.remove(temp_image_name)
            messages.warning(request, 'Driver Face not detected in the captured image')
    else:
        messages.warning(request, 'Method Not Allowed')
        
    return redirect(reverse('incident-list'))
