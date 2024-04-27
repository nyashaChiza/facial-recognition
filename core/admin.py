from django.contrib import admin
from .models import Citizen, Incident, CitizenImage

class IncidentsInline(admin.TabularInline):
    model = Incident
    extra = 1

class CitizenImagesInline(admin.TabularInline):
    model = CitizenImage
    extra = 1

@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'id_type', 'id_number', 'is_blacklisted')
    search_fields = ['first_name', 'last_name', 'id_number']
    inlines = [IncidentsInline, CitizenImagesInline]
    list_filter = ('is_blacklisted',)

@admin.register(Incident)
class IncidentsAdmin(admin.ModelAdmin):
    list_display = ('citizen','title', 'comment', 'created', 'updated')
    list_filter = ('created', 'updated')
    search_fields = ['citizen__first_name', 'citizen__last_name', 'comment']

@admin.register(CitizenImage)
class CitizenImagesAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'image', 'created', 'updated')
    list_filter = ('created', 'updated')
    search_fields = ['citizen__first_name', 'citizen__last_name']

