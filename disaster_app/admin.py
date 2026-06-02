from django.contrib import admin
from .models import Incident, HazardImage, SensorData


class HazardImageInline(admin.TabularInline):
    model = HazardImage
    extra = 1


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'status',
        'created_by',
        'created_at'
    )
    list_filter = (
        'status',
        'created_at'
    )
    search_fields = (
        'title',
        'description'
    )
    inlines = [HazardImageInline]


@admin.register(HazardImage)
class HazardImageAdmin(admin.ModelAdmin):
    list_display = (
        'incident',
        'caption'
    )


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = (
        'location',
        'water_level',
        'rainfall',
        'temperature',
        'severity',
        'created_at'
    )

    list_filter = (
        'severity',
        'created_at'
    )

    search_fields = (
        'location',
    )

    ordering = (
        '-created_at',
    )