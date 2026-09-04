from django.urls import reverse
from django.contrib import messages
from .models import Config
from .forms import CitizenSearchForm, ConfigForm
from django.views.generic import TemplateView, UpdateView


class IndexView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CitizenSearchForm()
        context['config'] = Config.objects.first()
        return context


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
