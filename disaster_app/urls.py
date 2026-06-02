from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [

    # =========================
    # UI PAGES
    # =========================
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'incident/create/',
        views.create_incident,
        name='create_incident'
    ),

    # =========================
    # SYSTEM HEALTH
    # =========================
    path(
        'health/',
        views.health_check,
        name='health_check'
    ),

    # =========================
    # INCIDENT APIs
    # =========================
    path(
        'api/incidents/',
        views.incident_list_api,
        name='incident_list_api'
    ),

    path(
        'api/incidents/create/',
        views.incident_create_api,
        name='incident_create_api'
    ),

    # =========================
    # SENSOR APIs
    # =========================
    path(
        'api/sensors/',
        views.sensor_list_api,
        name='sensor_list_api'
    ),

    path(
        'api/sensors/create/',
        views.sensor_create_api,
        name='sensor_create_api'
    ),

    # =========================
    # HAZARD REPORT APIs
    # =========================
    path(
        'api/hazards/',
        views.hazard_list_api,
        name='hazard_list_api'
    ),

    path(
        'api/hazards/create/',
        views.hazard_create_api,
        name='hazard_create_api'
    ),

    # =========================
    # JWT AUTH
    # =========================
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]