from django.contrib import admin
from .models import Citizen, Incident, CitizenImage, Config


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
    list_display = ('citizen', 'title', 'comment', 'created', 'updated')
    list_filter = ('created', 'updated')
    search_fields = ['citizen__first_name', 'citizen__last_name', 'comment']


@admin.register(CitizenImage)
class CitizenImagesAdmin(admin.ModelAdmin):
    list_display = ('citizen', 'image', 'created', 'updated')
    list_filter = ('created', 'updated')
    search_fields = ['citizen__first_name', 'citizen__last_name']


class ConfigAdmin(admin.ModelAdmin):
    list_display = (
        'minimum_detection_threshold', 'maximum_detection_threshold',
        'maximum_points_threshold', 'created', 'updated',
    )
    search_fields = ('minimum_detection_threshold', 'maximum_detection_threshold', 'maximum_points_threshold')
    list_filter = ('created', 'updated')
    readonly_fields = ('created', 'updated')
    fieldsets = (
        (None, {
            'fields': ('minimum_detection_threshold', 'maximum_detection_threshold', 'maximum_points_threshold')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        # Config is a singleton in practice: every view that reads it uses
        # Config.objects.first(), and the migration that seeds the first
        # row assumes there's only ever one. A second row via the admin
        # would silently desync "first()" reads from whichever row the
        # config-update form actually edited.
        return not Config.objects.exists()


admin.site.register(Config, ConfigAdmin)
