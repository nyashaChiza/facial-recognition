import os

from django.urls import reverse
from django.contrib import messages
from core.helpers import find_face
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView
from core.services import InvalidImageDataError, decode_captured_image, write_temp_image

from .models import Incident, Config
from .forms import IncidentForm


class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incidents/create.html'


class IncidentListView(ListView):
    model = Incident
    context_object_name = 'incidents'
    template_name = 'incidents/index.html'


class IncidentDetailView(DetailView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incidents/detail.html'


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
