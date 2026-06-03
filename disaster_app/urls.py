from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'dispatcher-dashboard/',
        views.dispatcher_dashboard,
        name='dispatcher_dashboard'
    ),

    path(
        'public-dashboard/',
        views.public_dashboard,
        name='public_dashboard'
    ),

    path(
        'incidents/',
        views.incident_management,
        name='incident_management'
    ),

    path(
        'hazard-report/',
        views.hazard_report_form,
        name='hazard_report_form'
    ),

    path(
        'sensors/',
        views.sensor_monitoring,
        name='sensor_monitoring'
    ),

    path(
        'reports/',
        views.reports_analytics,
        name='reports_analytics'
    ),

    path(
        'audit-log/',
        views.audit_log,
        name='audit_log'
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

    path(
        'api/incidents/<int:pk>/',
        views.incident_detail_api,
        name='incident_detail_api'
    ),

    path(
        'api/incidents/bulk-update-status/',
        views.bulk_update_status,
        name='bulk_update_status'
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

    path(
        'health-check/',
        views.health_check,
        name='health_check'
    ),
]
