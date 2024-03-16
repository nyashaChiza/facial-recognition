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
    generate_incident_report,
    webcam_view, capture_incident,
    capture_image,
    capture_driver
    
)

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('citizens/', CitizenListView.as_view(), name='citizen-list'),
    path('citizens/create/', CitizenCreateView.as_view(), name='citizen-create'),
    path('captute/driver/', capture_driver, name='driver-create'),
    # path('incident/create/', IncidentCreateView.as_view(), name='incident-create'),
    path('incident/create/', capture_incident, name='incident-create'),
    path('citizen/detail/<int:pk>', CitizenDetailView.as_view(), name='citizen-detail'),
    path('incident/detail/<int:pk>', IncidentDetailView.as_view(), name='incident-detail'),
    path('incidents/', IncidentListView.as_view(), name='incident-list'),
    path('images/', ImagesListView.as_view(), name='image-list'),
    path('search/', search_citizens, name='search_citizens'),
    path('generate_incident_report/<int:citizen_id>/', generate_incident_report, name='generate_incident_report'),
    path('webcam/', webcam_view, name='webcam_view'),
    
    path('capture-image/', capture_image, name='capture_image'),
    # Add other URL patterns as needed
]
