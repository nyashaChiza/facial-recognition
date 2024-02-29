from django.urls import path
from .views import (
    IndexView,
    CitizenListView,
    IncidentListView,
    ImagesListView,
    CitizenDetailView,
    IncidentDetailView,
    IncidentCreateView,
    CitizenCreateView,
    search_citizens,
    generate_incident_report
)

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('citizens/', CitizenListView.as_view(), name='citizen-list'),
    path('citizens/create/', CitizenCreateView.as_view(), name='citizen-create'),
    path('incident/create/', IncidentCreateView.as_view(), name='incident-create'),
    path('citizen/detail/<int:pk>', CitizenDetailView.as_view(), name='citizen-detail'),
    path('incident/detail/<int:pk>', IncidentDetailView.as_view(), name='incident-detail'),
    path('incidents/', IncidentListView.as_view(), name='incident-list'),
    path('images/', ImagesListView.as_view(), name='image-list'),
    path('search/', search_citizens, name='search_citizens'),
    path('generate_incident_report/<int:citizen_id>/', generate_incident_report, name='generate_incident_report'),
    # Add other URL patterns as needed
]
