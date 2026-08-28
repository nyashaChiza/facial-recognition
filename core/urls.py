from django.urls import path
from .views import (
    IndexView,
    CitizenListView,
    ImagesListView,
    CitizenDetailView,
    CitizenCreateView,
    search_citizens,
    capture_driver,
    edit_citizen,
    blacklist_citizen,
    reinstate_citizen,
    BlacklistedCitizenListView,
    ConfigUpdateView
)
from .views_reports import generate_incident_report
from .views_incidents import (
    IncidentListView,
    IncidentDetailView,
    IncidentCreateView,
    capture_incident,
)

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('citizens/', CitizenListView.as_view(), name='citizen-list'),
    path('blacklist/', BlacklistedCitizenListView.as_view(), name='blacklist'),

    path('citizens/create/', CitizenCreateView.as_view(), name='citizen-create'),
    path('capture/driver/', capture_driver, name='driver-create'),

    path('incident/create/', IncidentCreateView.as_view(), name='incident-create'),
    path('capture/incident/', capture_incident, name='incident-capture'),
    path('citizen/detail/<int:pk>', CitizenDetailView.as_view(), name='citizen-detail'),
    path('citizen/edit/<int:pk>', edit_citizen, name='citizen-update'),

    path('config/set/<int:pk>', ConfigUpdateView.as_view(), name='config-update'),
    path('incident/detail/<int:pk>', IncidentDetailView.as_view(), name='incident-detail'),
    path('incidents/', IncidentListView.as_view(), name='incident-list'),

    path('images/', ImagesListView.as_view(), name='image-list'),
    path('search/', search_citizens, name='search_citizens'),

    path('generate_incident_report/<int:citizen_id>/', generate_incident_report, name='generate_incident_report'),
    path('blacklist-driver/<int:citizen_id>/', blacklist_citizen, name='blacklist-driver'),
    path('reinstate-driver/<int:citizen_id>/', reinstate_citizen, name='reinstate-driver'),

    # Add other URL patterns as needed
]
