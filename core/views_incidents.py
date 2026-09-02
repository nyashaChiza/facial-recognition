import os

from django.urls import reverse
from django.contrib import messages
from core.helpers import find_face
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView
from core.services import InvalidImageDataError, decode_captured_image, write_temp_image
from core.services_incidents import record_incident
from core.validators import PayloadValidationError, validate_capture_payload

from .models import Incident
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
        try:
            image_data = validate_capture_payload(request.POST)
            ext, decoded = decode_captured_image(image_data)
        except (PayloadValidationError, InvalidImageDataError) as e:
            messages.warning(request, str(e))
            return redirect(reverse('incident-list'))

        temp_image_name = write_temp_image(decoded, ext)
        try:
            match = find_face(temp_image_name)
        finally:
            os.remove(temp_image_name)

        if match is None:
            messages.warning(request, 'No face detected in the captured image, please try again')
            return redirect(request.path)

        if not match['status']:
            messages.warning(
                request,
                'This face does not match any registered driver. Please register the driver first.'
            )
            return redirect(request.path)

        driver = match['driver']
        result = record_incident(driver, request.POST)
        if result['status'] == 'saved':
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
        messages.warning(request, 'Method Not Allowed')

    return redirect(reverse('incident-list'))
