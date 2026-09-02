from django.db import models
from django.urls import reverse
from django.contrib import messages
from .models import Citizen, CitizenImage, Config
from .forms import BlacklistForm, CitizenSearchForm, CitizenForm, ConfigForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from core.services import InvalidImageDataError, process_driver_capture, reinstate_driver, update_driver_photo
from core.validators import PayloadValidationError, validate_capture_payload


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


@require_POST
def reinstate_citizen(request, citizen_id):
    reinstate_driver(citizen_id)
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


class CitizenCreateView(CreateView):
    model = Citizen
    form_class = CitizenForm
    template_name = 'citizens/create.html'


def edit_citizen(request, pk):
    citizen = get_object_or_404(Citizen, pk=pk)

    if request.method == 'POST':
        form = CitizenForm(request.POST, instance=citizen)
        if form.is_valid():
            citizen = form.save()
            image_data = request.POST.get('image_data')
            if image_data:
                try:
                    update_driver_photo(citizen, image_data)
                except InvalidImageDataError as e:
                    messages.warning(request, f'Driver details saved, but photo was not updated: {e}')
                    return redirect('citizen-detail', pk=citizen.pk)
            messages.success(request, f'{citizen} updated successfully')
            return redirect('citizen-detail', pk=citizen.pk)
        else:
            messages.warning(request, 'Invalid Driver Information')
    else:
        form = CitizenForm(instance=citizen)

    return render(request, 'citizens/edit.html', {'form': form, 'citizen': citizen})


class ImagesListView(ListView):
    model = CitizenImage
    context_object_name = 'images'
    template_name = 'images/index.html'


def search_citizens(request):
    search_query = request.GET.get('search_query', '')
    citizens: models.QuerySet | list = []
    if search_query:
        terms = [term.strip() for term in search_query.split(',') if term.strip()]
        query = models.Q()
        for term in terms:
            query |= (
                models.Q(first_name__icontains=term) |
                models.Q(last_name__icontains=term) |
                models.Q(id_number__icontains=term)
            )
        citizens = Citizen.objects.filter(query).distinct() if terms else []
    return render(request, 'citizens/search_results.html', {'citizens': citizens})


def capture_driver(request):
    if request.method == 'POST':
        citizen_form = CitizenForm(request.POST)
        if citizen_form.is_valid():
            citizen = citizen_form.save(commit=False)
            try:
                image_data = validate_capture_payload(request.POST)
                result = process_driver_capture(citizen, image_data)
            except (PayloadValidationError, InvalidImageDataError) as e:
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
