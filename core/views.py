import os

from django.db import models
from django.urls import reverse
from reportlab.pdfgen import canvas
from django.contrib import messages
from django.http import HttpResponse
from core.helpers import find_face
from .models import Citizen, Incident, CitizenImage, Config
from .forms import BlacklistForm, CitizenSearchForm, CitizenForm, IncidentForm, ConfigForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from core.services import InvalidImageDataError, decode_captured_image, write_temp_image, process_driver_capture


class IndexView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CitizenSearchForm()
        context['config'] = Config.objects.first()
        return context


class CitizenListView(ListView):
    model = Citizen
    context_object_name = 'citizens'
    template_name = 'citizens/index.html'


class BlacklistedCitizenListView(ListView):
    model = Citizen
    context_object_name = 'citizens'
    template_name = 'citizens/blacklist.html'

    def get_queryset(self):
        return super().get_queryset().filter(is_blacklisted=True).all()


class CitizenDetailView(DetailView):
    model = Citizen
    context_object_name = 'citizen'
    template_name = 'citizens/detail.html'


class IncidentDetailView(DetailView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incidents/detail.html'


def reinstate_citizen(request, citizen_id):
    # Retrieve the citizen object
    citizen = Citizen.objects.get(pk=citizen_id)

    if request.method == 'GET':
        citizen.is_blacklisted = False
        citizen.blacklist_reason = ""
        citizen.save()
    return redirect('citizen-list')


def blacklist_citizen(request, citizen_id):
    # Retrieve the citizen object
    citizen = Citizen.objects.get(pk=citizen_id)

    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = BlacklistForm(request.POST, instance=citizen)
        if form.is_valid():
            # Save the form
            citizen.is_blacklisted = True
            citizen.blacklist_reason = form.cleaned_data['blacklist_reason']
            citizen.save()
            return redirect('citizen-detail', pk=citizen_id)  # Redirect to the citizen detail page
    else:
        # If it's a GET request, create a blank form
        form = BlacklistForm(instance=citizen)

    return render(request, 'citizens/blacklist_form.html', {'form': form, 'citizen': citizen})


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
    p.drawString(100, 800, f"Incident Report for {citizen.first_name} {citizen.last_name} ")
    p.drawString(100, 780, f"Is Blacklist : {'Yes' if citizen.is_blacklisted else 'No'} ")
    p.drawString(100, 760, f"ID Type: {citizen.id_type} ")
    p.drawString(100, 740, f"ID Number: {citizen.id_number} ")
    p.drawString(100, 720, f"Total Points: {citizen.get_total_points()} ")

    if citizen.is_blacklisted:
        p.drawString(100, 700, f"Blacklist Reason: {citizen.blacklist_reason} ")
    y_position = 680
    for incident in incidents:
        y_position -= 20
        p.drawString(100, y_position, f"Title: {incident.title}")
        y_position -= 15
        p.drawString(100, y_position, f"Points: {incident.points}")
        y_position -= 20
        p.drawString(100, y_position, f"Vehicle Reg Number: {incident.vehicle_registration_number}")
        y_position -= 15
        p.drawString(100, y_position, f"Location: {incident.location}")
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
            try:
                result = process_driver_capture(citizen, image_data)
            except InvalidImageDataError as e:
                messages.warning(request, str(e))
            else:
                if result['status'] == 'duplicate':
                    driver = result['detection'].get('driver')
                    messages.warning(
                        request,
                        'A face is detected in the captured image. '
                        f'Please make sure it belongs to the driver {driver}.'
                    )
                else:
                    messages.success(request, 'Driver added successfully')
        else:
            messages.warning(request, 'Invalid Driver Information')
    else:
        messages.warning(request, 'Method Not Allowed')

    return redirect(reverse('citizen-list'))


def capture_incident(request):
    if request.method == 'POST':
        image_data = request.POST.get('image_data')
        try:
            ext, decoded = decode_captured_image(image_data)
        except InvalidImageDataError as e:
            messages.warning(request, str(e))
            return redirect(reverse('incident-list'))

        temp_image_name = write_temp_image(decoded, ext)
        try:
            driver = find_face(temp_image_name)
        finally:
            os.remove(temp_image_name)

        if driver:
            driver = driver.get('driver')
            incident_form = IncidentForm(request.POST)
            if incident_form.is_valid():
                incident = incident_form.save(commit=False)
                incident.citizen = driver
                incident.save()
                config = Config.objects.first()
                max_points = config.maximum_points_threshold if config else 1
                if incident.citizen.get_total_points() > max_points:
                    incident.citizen.is_blacklisted = True
                    incident.citizen.blacklist_reason = 'Points Exceeded Limit'
                    incident.citizen.save()
                if driver.is_blacklisted:
                    messages.warning(
                        request,
                        f'Incident for {driver} saved successfully (Please Note This is a blacklisted Driver)'
                    )
                else:
                    messages.success(request, f'Incident for {driver} saved successfully')

            else:
                messages.warning(request, f'Invalid Driver Information for {driver}')
        else:
            messages.warning(request, 'Driver Face not detected in the captured image, please try again')
            return redirect(request.path)
    else:
        messages.warning(request, 'Method Not Allowed')

    return redirect(reverse('incident-list'))


class ConfigUpdateView(UpdateView):
    template_name = 'config/update.html'
    model = Config
    form_class = ConfigForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = Config.objects.first()
        return context

    def get_success_url(self):
        messages.success(self.request, 'System configuration updated successfully')
        return reverse('home')
