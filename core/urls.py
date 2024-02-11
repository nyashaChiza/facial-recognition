from django.urls import path
from .views import IndexView, CitizenListView, IncidentListView, ImagesListView, CitizenDetailView,IncidentDetailView

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('citizens/', CitizenListView.as_view(), name='citizen-list'),
    path('citizen/detail/<int:pk>', CitizenDetailView.as_view(), name='citizen-detail'),
    path('incident/detail/<int:pk>', IncidentDetailView.as_view(), name='incident-detail'),
    path('incidents/', IncidentListView.as_view(), name='incident-list'),
    path('images/', ImagesListView.as_view(), name='image-list'),
    # Add other URL patterns as needed
]
